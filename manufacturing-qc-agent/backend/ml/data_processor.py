"""
Pandas-based data processing pipeline for sensor readings.
Handles cleaning, feature engineering, rolling statistics.
"""
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
from config import QUALITY_THRESHOLDS

logger = logging.getLogger(__name__)


class DataProcessor:
    """Transforms raw sensor readings into model-ready feature frames."""

    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self._buffer: dict[str, list[dict]] = {}    # keyed by process_line

    # ── Buffering ────────────────────────────────────────────────────────────

    def add_reading(self, process_line: str, reading: dict):
        """Append a reading to the rolling buffer."""
        if process_line not in self._buffer:
            self._buffer[process_line] = []
        self._buffer[process_line].append({**reading, "timestamp": datetime.utcnow()})
        # Keep only last 1000 readings per line
        if len(self._buffer[process_line]) > 1000:
            self._buffer[process_line] = self._buffer[process_line][-1000:]

    def get_buffer_df(self, process_line: str) -> pd.DataFrame:
        data = self._buffer.get(process_line, [])
        if not data:
            return pd.DataFrame()
        return pd.DataFrame(data)

    # ── Feature Engineering ──────────────────────────────────────────────────

    def build_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Build a feature frame from raw sensor readings DataFrame.
        Expects columns: sensor_type, value, process_line, timestamp.
        Returns one row per timestamp with one column per sensor type.
        """
        if df.empty:
            return pd.DataFrame()

        df = df.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")

        # Pivot to wide format
        pivot = df.pivot_table(
            index="timestamp", columns="sensor_type", values="value", aggfunc="last"
        )
        pivot = pivot.reindex(columns=list(QUALITY_THRESHOLDS.keys()), fill_value=np.nan)
        pivot = pivot.fillna(method="ffill").fillna(0.0)

        # Rolling statistics
        for col in pivot.columns:
            pivot[f"{col}_mean{self.window_size}"] = (
                pivot[col].rolling(self.window_size, min_periods=1).mean()
            )
            pivot[f"{col}_std{self.window_size}"] = (
                pivot[col].rolling(self.window_size, min_periods=1).std().fillna(0)
            )
            pivot[f"{col}_lag1"] = pivot[col].shift(1).fillna(0)
            pivot[f"{col}_delta"] = pivot[col].diff().fillna(0)

        # Time features
        pivot["hour_of_day"]   = pivot.index.hour
        pivot["minute_of_hour"] = pivot.index.minute

        return pivot.reset_index()

    def get_latest_snapshot(self, process_line: str) -> dict:
        """Return the most-recent value for every sensor on a process line."""
        buf = self._buffer.get(process_line, [])
        if not buf:
            return {}
        df = pd.DataFrame(buf)
        if "sensor_type" not in df.columns or "value" not in df.columns:
            return {}
        latest = df.groupby("sensor_type")["value"].last().to_dict()
        return latest

    # ── SPC Control Chart Data ───────────────────────────────────────────────

    def compute_control_chart(self, df: pd.DataFrame, sensor_type: str) -> dict:
        """
        Compute X-bar and R-chart data for a sensor.
        Returns lists suitable for Recharts.
        """
        sensor_df = df[df["sensor_type"] == sensor_type].copy()
        if sensor_df.empty or len(sensor_df) < 4:
            return {}

        sensor_df = sensor_df.sort_values("timestamp").reset_index(drop=True)
        values = sensor_df["value"].values

        t = QUALITY_THRESHOLDS.get(sensor_type, {})
        ucl = t.get("ucl", float(np.mean(values) + 3 * np.std(values)))
        lcl = t.get("lcl", float(np.mean(values) - 3 * np.std(values)))

        # Subgroup size of 5 (standard SPC)
        subgroup = 5
        groups = [values[i:i+subgroup] for i in range(0, len(values), subgroup) if len(values[i:i+subgroup]) == subgroup]
        xbar_vals = [float(np.mean(g)) for g in groups]
        r_vals    = [float(np.max(g) - np.min(g)) for g in groups]

        return {
            "xbar": {
                "data":   xbar_vals,
                "mean":   round(float(np.mean(xbar_vals)), 4) if xbar_vals else 0,
                "ucl":    ucl,
                "lcl":    lcl,
            },
            "r_chart": {
                "data":   r_vals,
                "mean":   round(float(np.mean(r_vals)), 4) if r_vals else 0,
                "ucl_r":  round(float(np.mean(r_vals) * 2.114), 4) if r_vals else 0,
                "lcl_r":  0.0,
            },
            "labels":  list(range(len(xbar_vals))),
            "violations": [
                i for i, v in enumerate(xbar_vals)
                if v > ucl or v < lcl
            ],
        }

    # ── Summary Statistics ───────────────────────────────────────────────────

    def summarise(self, df: pd.DataFrame, sensor_type: str) -> dict:
        """Return descriptive statistics for a sensor."""
        data = df[df["sensor_type"] == sensor_type]["value"] if "sensor_type" in df.columns else df.get(sensor_type, pd.Series())
        if data.empty:
            return {}
        return {
            "min":    round(float(data.min()),  4),
            "max":    round(float(data.max()),  4),
            "mean":   round(float(data.mean()), 4),
            "std":    round(float(data.std()),  4),
            "median": round(float(data.median()), 4),
            "count":  int(data.count()),
        }

    def normalise_value(self, sensor_type: str, value: float) -> float:
        """Normalise a reading to [0,1] within its configured range."""
        t = QUALITY_THRESHOLDS.get(sensor_type)
        if not t or t["max"] == t["min"]:
            return 0.5
        return round(float(np.clip((value - t["min"]) / (t["max"] - t["min"]), 0, 1)), 4)


_processor: Optional[DataProcessor] = None


def get_data_processor() -> DataProcessor:
    global _processor
    if _processor is None:
        _processor = DataProcessor()
    return _processor
