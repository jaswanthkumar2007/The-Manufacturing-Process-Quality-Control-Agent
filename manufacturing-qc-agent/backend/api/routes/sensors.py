"""
Sensor data API routes.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from db.crud import create_sensor_reading, get_recent_readings, get_anomaly_readings
from mqtt.client import get_mqtt_client
from ml.anomaly_detector import get_anomaly_detector
from ml.data_processor import get_data_processor
from config import QUALITY_THRESHOLDS, PROCESS_LINES, SENSOR_TOPICS
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/sensors", tags=["Sensors"])


class SensorReadingIn(BaseModel):
    sensor_type:  str
    value:        float
    unit:         str = ""
    process_line: str
    sensor_id:    Optional[str] = None


@router.get("/latest")
async def get_latest_readings():
    """Return the latest reading for every sensor on every process line."""
    client = get_mqtt_client()
    return {"readings": client.get_latest_readings()}


@router.get("/latest/{process_line}")
async def get_latest_for_line(process_line: str):
    """Return the latest readings for a specific process line."""
    client = get_mqtt_client()
    if hasattr(client, "_simulator") and client._simulator:
        data = client._simulator.get_latest_for_line(process_line)
    else:
        all_data = client.get_latest_readings()
        data = {k.split(":")[1]: v for k, v in all_data.items()
                if k.startswith(f"{process_line}:")}
    return {"process_line": process_line, "readings": data}


@router.get("/history")
async def get_sensor_history(
    sensor_type:  Optional[str] = None,
    process_line: Optional[str] = None,
    limit:        int = Query(100, le=500),
    db: AsyncSession = Depends(get_db),
):
    readings = await get_recent_readings(db, sensor_type, process_line, limit)
    return {
        "readings": [
            {
                "id":           r.id,
                "sensor_type":  r.sensor_type,
                "value":        r.value,
                "unit":         r.unit,
                "process_line": r.process_line,
                "is_anomaly":   r.is_anomaly,
                "timestamp":    r.timestamp.isoformat(),
            }
            for r in readings
        ]
    }


@router.get("/anomalies")
async def get_anomalies(
    hours: int = Query(24, le=168),
    db: AsyncSession = Depends(get_db),
):
    readings = await get_anomaly_readings(db, hours)
    return {
        "anomalies": [
            {
                "sensor_type":   r.sensor_type,
                "value":         r.value,
                "process_line":  r.process_line,
                "anomaly_score": r.anomaly_score,
                "timestamp":     r.timestamp.isoformat(),
            }
            for r in readings
        ],
        "count": len(readings),
    }


@router.get("/thresholds")
async def get_thresholds():
    return {"thresholds": QUALITY_THRESHOLDS}


@router.get("/process-lines")
async def get_process_lines():
    return {"process_lines": PROCESS_LINES}


@router.get("/control-chart/{process_line}/{sensor_type}")
async def get_control_chart(
    process_line: str,
    sensor_type: str,
    db: AsyncSession = Depends(get_db),
):
    readings = await get_recent_readings(db, sensor_type, process_line, limit=200)
    processor = get_data_processor()
    import pandas as pd
    df = pd.DataFrame([
        {"sensor_type": r.sensor_type, "value": r.value, "timestamp": r.timestamp}
        for r in readings
    ])
    chart_data = processor.compute_control_chart(df, sensor_type) if not df.empty else {}
    return {"sensor_type": sensor_type, "process_line": process_line, "chart": chart_data}


@router.post("/ingest")
async def ingest_reading(
    reading: SensorReadingIn,
    db: AsyncSession = Depends(get_db),
):
    """Manually ingest a sensor reading (used for testing)."""
    detector  = get_anomaly_detector()
    anomaly   = detector.get_sensor_anomaly(reading.sensor_type, reading.value)
    processor = get_data_processor()
    processor.add_reading(reading.process_line, {
        "sensor_type": reading.sensor_type,
        "value":       reading.value,
    })
    record = await create_sensor_reading(db, {
        "sensor_id":     reading.sensor_id or f"{reading.process_line}_{reading.sensor_type}",
        "sensor_type":   reading.sensor_type,
        "process_line":  reading.process_line,
        "value":         reading.value,
        "unit":          reading.unit,
        "is_anomaly":    anomaly["is_anomaly"],
        "anomaly_score": anomaly["score"],
    })
    return {"id": record.id, "is_anomaly": anomaly["is_anomaly"]}
