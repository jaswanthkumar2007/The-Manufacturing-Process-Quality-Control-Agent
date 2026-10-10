"""
MQTT sensor data simulator.
Generates realistic sensor readings with noise and periodic anomalies.
Publishes to manufacturing/sensors/<sensor_type> topics.
"""
import json
import math
import random
import logging
import threading
import time
from datetime import datetime
from config import get_settings, SENSOR_TOPICS, QUALITY_THRESHOLDS, PROCESS_LINES

logger = logging.getLogger(__name__)
settings = get_settings()


class SensorSimulator:
    """
    Simulates 8 sensor types across 4 process lines.
    Publishes real-looking data with drift and occasional anomalies.
    """

    def __init__(self):
        self._running = False
        self._thread: threading.Thread | None = None
        self._tick = 0
        self._callbacks: list = []             # Called with (topic, payload)
        self._latest: dict = {}                # Cache of latest readings

        # Base values per process line
        self._base = {
            line: {
                "temperature": random.uniform(55, 70),
                "pressure":    random.uniform(4.0, 7.0),
                "vibration":   random.uniform(0.5, 2.0),
                "humidity":    random.uniform(40, 55),
                "speed":       random.uniform(800, 1800),
                "defect_rate": random.uniform(0.5, 1.5),
                "torque":      random.uniform(20, 60),
                "flow_rate":   random.uniform(5, 12),
            }
            for line in PROCESS_LINES
        }

    def on_message(self, callback):
        """Register a callback for simulated messages."""
        self._callbacks.append(callback)

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("Sensor simulator started")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    def _run(self):
        while self._running:
            for line in PROCESS_LINES:
                readings = self._generate_reading(line)
                for sensor_type, value in readings.items():
                    topic = f"{settings.mqtt_topic_prefix}/{sensor_type}"
                    payload = {
                        "sensor_type":  sensor_type,
                        "value":        value,
                        "unit":         self._unit(sensor_type),
                        "process_line": line,
                        "timestamp":    datetime.utcnow().isoformat(),
                        "sensor_id":    f"{line}_{sensor_type}",
                    }
                    self._latest[f"{line}:{sensor_type}"] = payload
                    for cb in self._callbacks:
                        try:
                            cb(topic, json.dumps(payload))
                        except Exception as exc:
                            logger.error("Simulator callback error: %s", exc)
            self._tick += 1
            time.sleep(1.5)

    def _generate_reading(self, line: str) -> dict[str, float]:
        base = self._base[line]
        readings = {}
        t = self._tick

        # Inject an anomaly every ~120 ticks on a random line/sensor
        inject_anomaly = (
            t > 0
            and t % random.randint(100, 140) == 0
            and line == random.choice(PROCESS_LINES)
        )

        for sensor, base_val in base.items():
            thr = QUALITY_THRESHOLDS[sensor]
            span = thr["ucl"] - thr["lcl"]

            # Slow sinusoidal drift + Gaussian noise
            drift   = 0.05 * span * math.sin(2 * math.pi * t / 200)
            noise   = random.gauss(0, span * 0.02)
            new_val = base_val + drift + noise

            # Occasionally shift baseline slightly (simulate process change)
            if random.random() < 0.002:
                base[sensor] = new_val
                self._base[line][sensor] = new_val

            # Inject anomaly on one sensor
            if inject_anomaly and sensor == random.choice(list(base.keys())):
                direction = random.choice([-1, 1])
                new_val   = thr["ucl"] + direction * span * random.uniform(0.1, 0.4)

            readings[sensor] = round(
                max(thr["min"] * 0.95, min(thr["max"] * 1.05, new_val)),
                3,
            )

        return readings

    def _unit(self, sensor_type: str) -> str:
        units = {
            "temperature": "°C",
            "pressure":    "bar",
            "vibration":   "mm/s",
            "humidity":    "%RH",
            "speed":       "RPM",
            "defect_rate": "%",
            "torque":      "N·m",
            "flow_rate":   "L/min",
        }
        return units.get(sensor_type, "")

    def get_latest(self) -> dict:
        return dict(self._latest)

    def get_latest_for_line(self, process_line: str) -> dict:
        return {
            k.split(":")[1]: v
            for k, v in self._latest.items()
            if k.startswith(f"{process_line}:")
        }


_simulator: SensorSimulator | None = None


def get_simulator() -> SensorSimulator:
    global _simulator
    if _simulator is None:
        _simulator = SensorSimulator()
    return _simulator
