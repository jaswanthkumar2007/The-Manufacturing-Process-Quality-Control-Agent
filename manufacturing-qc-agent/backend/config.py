"""
Central configuration for the Manufacturing QC Agent backend.
All values are read from environment variables with sensible defaults.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────────────────────────
    app_name: str = "Manufacturing QC Agent"
    app_version: str = "1.0.0"
    debug: bool = False
    secret_key: str = "dev-secret-change-in-production"

    # ── IBM watsonx.ai ───────────────────────────────────────────────────────
    watsonx_api_key: Optional[str] = None
    watsonx_project_id: Optional[str] = None
    watsonx_url: str = "https://us-south.ml.cloud.ibm.com"
    granite_model_id: str = "ibm/granite-13b-instruct-v2"
    granite_max_tokens: int = 1024
    granite_temperature: float = 0.2
    granite_top_p: float = 0.9

    # ── Database ─────────────────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/manufacturing_qc"
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # ── MQTT ─────────────────────────────────────────────────────────────────
    mqtt_broker: str = "localhost"
    mqtt_port: int = 1883
    mqtt_username: Optional[str] = None
    mqtt_password: Optional[str] = None
    mqtt_keepalive: int = 60
    mqtt_topic_prefix: str = "manufacturing/sensors"
    mqtt_simulate: bool = True          # Use simulator when no real broker

    # ── ChromaDB ─────────────────────────────────────────────────────────────
    chroma_persist_dir: str = "./chroma_db"
    chroma_collection_name: str = "manufacturing_knowledge"

    # ── ML Models ────────────────────────────────────────────────────────────
    ml_models_dir: str = "./ml_models"
    anomaly_contamination: float = 0.05
    anomaly_n_estimators: int = 100

    # ── CORS ─────────────────────────────────────────────────────────────────
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Sensor topics
SENSOR_TOPICS = {
    "temperature":   "manufacturing/sensors/temperature",
    "pressure":      "manufacturing/sensors/pressure",
    "vibration":     "manufacturing/sensors/vibration",
    "humidity":      "manufacturing/sensors/humidity",
    "speed":         "manufacturing/sensors/speed",
    "defect_rate":   "manufacturing/sensors/defect_rate",
    "torque":        "manufacturing/sensors/torque",
    "flow_rate":     "manufacturing/sensors/flow_rate",
}

# Quality thresholds per sensor
QUALITY_THRESHOLDS = {
    "temperature": {"min": 18.0,  "max": 85.0,  "ucl": 80.0,  "lcl": 20.0},
    "pressure":    {"min": 1.0,   "max": 10.0,  "ucl": 9.5,   "lcl": 1.5},
    "vibration":   {"min": 0.0,   "max": 5.0,   "ucl": 4.5,   "lcl": 0.0},
    "humidity":    {"min": 30.0,  "max": 70.0,  "ucl": 65.0,  "lcl": 35.0},
    "speed":       {"min": 100.0, "max": 3000.0,"ucl": 2800.0,"lcl": 150.0},
    "defect_rate": {"min": 0.0,   "max": 5.0,   "ucl": 3.0,   "lcl": 0.0},
    "torque":      {"min": 5.0,   "max": 100.0, "ucl": 95.0,  "lcl": 6.0},
    "flow_rate":   {"min": 0.5,   "max": 20.0,  "ucl": 18.0,  "lcl": 1.0},
}

# Process lines
PROCESS_LINES = ["CNC_LINE_A", "INJECTION_MOLD_B", "PCB_ASSEMBLY_C", "WELDING_LINE_D"]
