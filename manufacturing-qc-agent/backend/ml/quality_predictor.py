"""
Quality prediction using RandomForest and GradientBoosting classifiers.
Predicts pass / fail / review quality outcome from sensor snapshot.
"""
import os
import logging
import numpy as np
import pandas as pd
import joblib
from typing import Optional
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from config import get_settings, QUALITY_THRESHOLDS

logger = logging.getLogger(__name__)
settings = get_settings()

QUALITY_LABELS = ["pass", "review", "fail"]
FEATURES = list(QUALITY_THRESHOLDS.keys())


class QualityPredictor:
    """Predicts manufacturing quality outcome from sensor readings."""

    def __init__(self):
        self.pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("clf",    RandomForestClassifier(
                n_estimators=200,
                max_depth=8,
                class_weight="balanced",
                random_state=42,
                n_jobs=-1,
            )),
        ])
        self.label_encoder = LabelEncoder().fit(QUALITY_LABELS)
        self._fitted = False
        self._model_path = os.path.join(settings.ml_models_dir, "quality_predictor.joblib")
        os.makedirs(settings.ml_models_dir, exist_ok=True)
        self._load_or_init()

    def _load_or_init(self):
        if os.path.exists(self._model_path):
            try:
                state = joblib.load(self._model_path)
                self.pipeline      = state["pipeline"]
                self.label_encoder = state["label_encoder"]
                self._fitted       = state["fitted"]
                logger.info("Quality predictor loaded from %s", self._model_path)
                return
            except Exception as exc:
                logger.warning("Could not load quality model: %s — retraining", exc)
        self._bootstrap_fit()

    def _bootstrap_fit(self):
        """Train on synthetic quality data for immediate availability."""
        rng = np.random.default_rng(42)
        n = 3000
        X, y = [], []
        thresholds = list(QUALITY_THRESHOLDS.values())

        for _ in range(n):
            row = []
            label_scores = []
            for t in thresholds:
                mid = (t["ucl"] + t["lcl"]) / 2
                span = (t["ucl"] - t["lcl"]) / 2
                # Bias toward normal range (pass)
                val = rng.normal(mid, span * 0.4)
                row.append(val)
                # Score how far from centre
                dist = abs(val - mid) / span
                label_scores.append(dist)

            avg_dist = np.mean(label_scores)
            if avg_dist < 0.5:
                label = "pass"
            elif avg_dist < 0.8:
                label = "review"
            else:
                label = "fail"

            # Random 10% noise
            if rng.random() < 0.1:
                label = rng.choice(QUALITY_LABELS)

            X.append(row)
            y.append(label)

        self.fit(np.array(X), np.array(y))
        logger.info("Quality predictor bootstrapped with synthetic data")

    def fit(self, X: np.ndarray, y: np.ndarray):
        y_enc = self.label_encoder.transform(y)
        self.pipeline.fit(X, y_enc)
        self._fitted = True
        joblib.dump(
            {"pipeline": self.pipeline, "label_encoder": self.label_encoder, "fitted": True},
            self._model_path,
        )
        logger.info("Quality predictor trained on %d samples", len(X))

    def predict(self, readings: dict) -> dict:
        """Predict quality outcome for a sensor snapshot dict."""
        if not self._fitted:
            return {"quality_grade": "unknown", "confidence": 0.0, "probabilities": {}}

        row = np.array([[readings.get(f, 0.0) for f in FEATURES]])
        pred_enc   = self.pipeline.predict(row)[0]
        proba      = self.pipeline.predict_proba(row)[0]
        label      = self.label_encoder.inverse_transform([pred_enc])[0]
        confidence = float(np.max(proba))

        proba_dict = {
            self.label_encoder.inverse_transform([i])[0]: round(float(p), 4)
            for i, p in enumerate(proba)
        }

        # Compute quality score 0–100
        quality_score = self._compute_quality_score(readings)

        return {
            "quality_grade":  label,
            "confidence":     round(confidence, 4),
            "quality_score":  quality_score,
            "probabilities":  proba_dict,
        }

    def _compute_quality_score(self, readings: dict) -> float:
        """Return a 0–100 quality score based on distance from control limits."""
        scores = []
        for sensor, val in readings.items():
            if sensor not in QUALITY_THRESHOLDS:
                continue
            t = QUALITY_THRESHOLDS[sensor]
            if t["ucl"] == t["lcl"]:
                continue
            mid  = (t["ucl"] + t["lcl"]) / 2
            half = (t["ucl"] - t["lcl"]) / 2
            dist = abs(val - mid) / half
            # 100 at centre, 0 at UCL/LCL
            score = max(0.0, 100.0 * (1.0 - dist))
            scores.append(score)
        return round(float(np.mean(scores)) if scores else 0.0, 2)

    def get_feature_importance(self) -> dict:
        """Return feature importance from the RandomForest."""
        clf = self.pipeline.named_steps["clf"]
        if hasattr(clf, "feature_importances_"):
            return {
                FEATURES[i]: round(float(v), 4)
                for i, v in enumerate(clf.feature_importances_)
            }
        return {}


_predictor: Optional[QualityPredictor] = None


def get_quality_predictor() -> QualityPredictor:
    global _predictor
    if _predictor is None:
        _predictor = QualityPredictor()
    return _predictor
