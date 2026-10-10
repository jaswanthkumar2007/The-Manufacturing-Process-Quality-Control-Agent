"""
MQTT client — subscribes to real broker or falls back to simulator.
Bridges MQTT messages into the application event bus.
"""
import json
import logging
import threading
from typing import Callable, Optional
from config import get_settings, SENSOR_TOPICS

logger = logging.getLogger(__name__)
settings = get_settings()


class MQTTClient:
    """
    Wraps paho-mqtt. Falls back to the built-in simulator
    when MQTT_SIMULATE=true or broker is unreachable.
    """

    def __init__(self):
        self._callbacks: list[Callable[[str, dict], None]] = []
        self._connected = False
        self._client = None
        self._simulator = None

        if settings.mqtt_simulate:
            self._init_simulator()
        else:
            success = self._init_mqtt()
            if not success:
                logger.warning("MQTT broker unreachable — falling back to simulator")
                self._init_simulator()

    # ── Initialisation ───────────────────────────────────────────────────────

    def _init_mqtt(self) -> bool:
        try:
            import paho.mqtt.client as mqtt

            self._client = mqtt.Client(client_id="qc_agent_backend")
            if settings.mqtt_username:
                self._client.username_pw_set(settings.mqtt_username, settings.mqtt_password)

            self._client.on_connect    = self._on_connect
            self._client.on_message    = self._on_mqtt_message
            self._client.on_disconnect = self._on_disconnect

            self._client.connect(
                settings.mqtt_broker,
                settings.mqtt_port,
                settings.mqtt_keepalive,
            )
            self._client.loop_start()
            logger.info("MQTT client connected to %s:%d", settings.mqtt_broker, settings.mqtt_port)
            return True
        except Exception as exc:
            logger.error("MQTT init error: %s", exc)
            return False

    def _init_simulator(self):
        from mqtt.simulator import get_simulator
        self._simulator = get_simulator()
        self._simulator.on_message(self._on_sim_message)
        self._simulator.start()
        logger.info("MQTT simulator activated")

    # ── Callbacks ────────────────────────────────────────────────────────────

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._connected = True
            logger.info("MQTT connected — subscribing to %s/#", settings.mqtt_topic_prefix)
            client.subscribe(f"{settings.mqtt_topic_prefix}/#")
        else:
            logger.error("MQTT connection refused: rc=%d", rc)

    def _on_disconnect(self, client, userdata, rc):
        self._connected = False
        logger.warning("MQTT disconnected: rc=%d", rc)

    def _on_mqtt_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            self._dispatch(msg.topic, payload)
        except Exception as exc:
            logger.error("MQTT message parse error: %s", exc)

    def _on_sim_message(self, topic: str, raw: str):
        try:
            payload = json.loads(raw)
            self._dispatch(topic, payload)
        except Exception as exc:
            logger.error("Simulator message error: %s", exc)

    def _dispatch(self, topic: str, payload: dict):
        for cb in self._callbacks:
            try:
                cb(topic, payload)
            except Exception as exc:
                logger.error("MQTT dispatch error: %s", exc)

    # ── Public API ───────────────────────────────────────────────────────────

    def subscribe(self, callback: Callable[[str, dict], None]):
        """Register a callback for incoming sensor messages."""
        self._callbacks.append(callback)

    def publish(self, topic: str, payload: dict):
        """Publish a message to the MQTT broker (no-op in simulator mode)."""
        if self._client and self._connected:
            import json as _json
            self._client.publish(topic, _json.dumps(payload))

    def get_latest_readings(self) -> dict:
        """Return the latest reading snapshot from the simulator."""
        if self._simulator:
            return self._simulator.get_latest()
        return {}

    def stop(self):
        if self._client:
            self._client.loop_stop()
            self._client.disconnect()
        if self._simulator:
            self._simulator.stop()


_mqtt_client: Optional[MQTTClient] = None


def get_mqtt_client() -> MQTTClient:
    global _mqtt_client
    if _mqtt_client is None:
        _mqtt_client = MQTTClient()
    return _mqtt_client
