"""
Scikit-learn anomaly detection for manufacturing sensor data.
Uses IsolationForest (primary) and One-Class SVM (secondary).
"""
import os
import logging
import numpy as np
import pandas as pd
import joblib
from typing import Optional
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from config import get_settings, QUALITY_THRESHOLDS

logger = logging.getLogger(__name__)
settings = get_settings()


class AnomalyDetector:
    """Isolation Forest + One-Class SVM ensemble anomaly detector."""

    def __init__(self):
        self.iso_forest = IsolationForest(
            n_estimators=settings.anomaly_n_estimators,
            contamination=settings.anomaly_contamination,
            random_state=42,
            n_jobs=-1,
        )
        self.oc_svm = OneClassSVM(kernel="rbf", gamma="scale", nu=0.05)
        self.scaler = StandardScaler()
        self._fitted = False
        self._model_path = os.path.join(settings.ml_models_dir, "anomaly_detector.joblib")
        os.makedirs(settings.ml_models_dir, exist_ok=True)
        self._load_or_init()

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def _load_or_init(self):
        if os.path.exists(self._model_path):
            try:
                state = joblib.load(self._model_path)
                self.iso_forest = state["iso_forest"]
                self.oc_svm     = state["oc_svm"]
                self.scaler     = state["scaler"]
                self._fitted    = state["fitted"]
                logger.info("Anomaly detector loaded from %s", self._model_path)
                return
            except Exception as exc:
                logger.warning("Could not load model: %s — will retrain", exc)
        # Bootstrap with synthetic data so it's ready immediately
        self._bootstrap_fit()

    def _bootstrap_fit(self):
        """Fit on a synthetic normal distribution so predictions work immediately."""
        rng = np.random.default_rng(42)
        n_features = len(QUALITY_THRESHOLDS)
        X = rng.normal(loc=0, scale=1, size=(2000, n_features))
        # Inject 5% anomalies
        n_anomalies = int(2000 * 0.05)
        anomaly_idx = rng.choice(2000, n_anomalies, replace=False)
        X[anomaly_idx] += rng.uniform(3, 6, size=(n_anomalies, n_features))
        self.fit(X)
        logger.info("Anomaly detector bootstrapped with synthetic data")

    def fit(self, X: np.ndarray):
        X_scaled = self.scaler.fit_transform(X)
        self.iso_forest.fit(X_scaled)
        self.oc_svm.fit(X_scaled[:500])   # SVM is O(n²) — subsample
        self._fitted = True
        joblib.dump(
            {"iso_forest": self.iso_forest, "oc_svm": self.oc_svm,
             "scaler": self.scaler, "fitted": True},
            self._model_path,
        )

    def predict(self, readings: dict) -> dict:
        """
        Predict anomaly for a single sensor reading dict.
        readings keys: sensor names, values: floats.
        """
        if not self._fitted:
            return {"is_anomaly": False, "score": 0.0, "method": "unfitted"}

        feature_names = list(QUALITY_THRESHOLDS.keys())
        row = np.array([[readings.get(f, 0.0) for f in feature_names]], dtype=float)

        row_scaled = self.scaler.transform(row)
        iso_pred  = self.iso_forest.predict(row_scaled)[0]          # 1=normal, -1=anomaly
        iso_score = self.iso_forest.score_samples(row_scaled)[0]    # more negative = more anomalous
        svm_pred  = self.oc_svm.predict(row_scaled)[0]              # 1=normal, -1=anomaly

        # Combine: anomaly if either model flags
        is_anomaly = (iso_pred == -1) or (svm_pred == -1)

        # Threshold-based override (always flag out-of-bounds)
        for sensor, val in readings.items():
            if sensor in QUALITY_THRESHOLDS:
                t = QUALITY_THRESHOLDS[sensor]
                if val > t["ucl"] or val < t["lcl"]:
                    is_anomaly = True
                    break

        # Normalise score to 0–1 (higher = more anomalous)
        normalised_score = float(np.clip(1.0 - (iso_score + 0.5), 0, 1))

        return {
            "is_anomaly":   bool(is_anomaly),
            "score":        round(normalised_score, 4),
            "iso_prediction": int(iso_pred),
            "svm_prediction": int(svm_pred),
            "method":       "ensemble",
        }

    def predict_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """Predict anomaly for each row in a DataFrame."""
        feature_names = [c for c in QUALITY_THRESHOLDS if c in df.columns]
        if not feature_names:
            df["is_anomaly"] = False
            df["anomaly_score"] = 0.0
            return df

        X = df[feature_names].fillna(0).values
        X_scaled = self.scaler.transform(X)
        iso_preds  = self.iso_forest.predict(X_scaled)
        iso_scores = self.iso_forest.score_samples(X_scaled)

        df = df.copy()
        df["is_anomaly"]    = iso_preds == -1
        df["anomaly_score"] = np.clip(1.0 - (iso_scores + 0.5), 0, 1).round(4)
        return df

    def get_sensor_anomaly(self, sensor_type: str, value: float) -> dict:
        """Quick single-sensor anomaly check with threshold override."""
        t = QUALITY_THRESHOLDS.get(sensor_type)
        if not t:
            return {"is_anomaly": False, "score": 0.0}

        score = 0.0
        is_anomaly = False

        # Distance from nearest limit → score
        if value > t["ucl"]:
            score = min(1.0, (value - t["ucl"]) / (t["max"] - t["ucl"] + 1e-6))
            is_anomaly = True
        elif value < t["lcl"]:
            score = min(1.0, (t["lcl"] - value) / (t["lcl"] - t["min"] + 1e-6))
            is_anomaly = True
        else:
            # Small score even within limits based on how close to the centre
            mid = (t["ucl"] + t["lcl"]) / 2
            half = (t["ucl"] - t["lcl"]) / 2
            score = abs(value - mid) / half * 0.3   # max 0.3 when near limits

        return {"is_anomaly": is_anomaly, "score": round(score, 4)}


# Singleton
_detector: Optional[AnomalyDetector] = None


def get_anomaly_detector() -> AnomalyDetector:
    global _detector
    if _detector is None:
        _detector = AnomalyDetector()
    return _detector
