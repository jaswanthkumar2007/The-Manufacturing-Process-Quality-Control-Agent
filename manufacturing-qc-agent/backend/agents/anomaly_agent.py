"""
Anomaly Agent — runs ML detection and interprets results with Granite.
"""
import logging
from ml.anomaly_detector import get_anomaly_detector
from granite.client import get_granite_client
from config import QUALITY_THRESHOLDS

logger = logging.getLogger(__name__)

ANOMALY_SYSTEM = """You are a manufacturing anomaly analysis expert.
You receive sensor readings and anomaly detection results.
Provide:
1. A clear description of what the anomaly means
2. The likely root cause (use Ishikawa / 5-Why reasoning)
3. Immediate corrective actions (prioritised)
4. Preventive measures to avoid recurrence
Be concise. Use bullet points. Reference ISO 9001 or SPC rules where applicable."""


class AnomalyAgent:
    def __init__(self):
        self.detector = get_anomaly_detector()
        self.granite  = get_granite_client()

    def run(self, state: dict) -> dict:
        snapshot = state.get("sensor_snapshot", {})
        if not snapshot:
            state["anomaly_result"] = {"is_anomaly": False, "details": []}
            return state

        # Flatten snapshot to {sensor_type: value}
        flat = self._flatten_snapshot(snapshot)

        # Run ensemble detection
        ensemble_result = self.detector.predict(flat)

        # Per-sensor checks
        sensor_alerts = []
        for sensor, val in flat.items():
            r = self.detector.get_sensor_anomaly(sensor, val)
            if r["is_anomaly"]:
                t = QUALITY_THRESHOLDS.get(sensor, {})
                sensor_alerts.append({
                    "sensor":    sensor,
                    "value":     val,
                    "score":     r["score"],
                    "ucl":       t.get("ucl"),
                    "lcl":       t.get("lcl"),
                })

        is_anomaly = ensemble_result["is_anomaly"] or bool(sensor_alerts)
        interpretation = ""

        if is_anomaly:
            interpretation = self._interpret(flat, sensor_alerts, state["process_line"])

        state["anomaly_result"] = {
            "is_anomaly":     is_anomaly,
            "ensemble_score": ensemble_result.get("score", 0),
            "sensor_alerts":  sensor_alerts,
            "interpretation": interpretation,
        }
        return state

    def _flatten_snapshot(self, snapshot: dict) -> dict:
        flat = {}
        for k, v in snapshot.items():
            if isinstance(v, dict):
                flat[k] = float(v.get("value", 0))
            elif isinstance(v, (int, float)):
                flat[k] = float(v)
        return flat

    def _interpret(self, flat: dict, alerts: list, process_line: str) -> str:
        alert_lines = "\n".join(
            f"  - {a['sensor']}: {a['value']} (UCL={a['ucl']}, LCL={a['lcl']}, score={a['score']})"
            for a in alerts
        )
        readings_str = "\n".join(f"  {k}: {v}" for k, v in flat.items())

        prompt = (
            f"Process line: {process_line}\n\n"
            f"Sensor readings:\n{readings_str}\n\n"
            f"Anomalies detected:\n{alert_lines}\n\n"
            "Analyse these anomalies and provide root cause and corrective actions."
        )
        return self.granite.generate(prompt, system_prompt=ANOMALY_SYSTEM)
