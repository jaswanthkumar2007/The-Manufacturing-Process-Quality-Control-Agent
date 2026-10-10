"""
QC Analysis API routes — quality stats, anomaly summaries, predictions.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from db.crud import get_quality_stats, get_active_alerts, resolve_alert, create_alert
from ml.quality_predictor import get_quality_predictor
from ml.anomaly_detector import get_anomaly_detector
from mqtt.client import get_mqtt_client
from config import PROCESS_LINES, QUALITY_THRESHOLDS

router = APIRouter(prefix="/analysis", tags=["QC Analysis"])


@router.get("/quality-stats")
async def get_quality_statistics(
    hours: int = Query(24, le=168),
    db: AsyncSession = Depends(get_db),
):
    stats = await get_quality_stats(db, hours)
    return {"stats": stats, "hours": hours}


@router.get("/predict/{process_line}")
async def predict_quality(process_line: str):
    """Predict quality for the current sensor snapshot."""
    client    = get_mqtt_client()
    snapshot  = client.get_latest_readings()
    flat_snap = {}
    for k, v in snapshot.items():
        if not k.startswith(f"{process_line}:"):
            continue
        sensor = k.split(":")[1]
        if isinstance(v, dict):
            flat_snap[sensor] = float(v.get("value", 0))
        elif isinstance(v, (int, float)):
            flat_snap[sensor] = float(v)

    predictor = get_quality_predictor()
    result    = predictor.predict(flat_snap)
    importance = predictor.get_feature_importance()

    return {
        "process_line":     process_line,
        "prediction":       result,
        "feature_importance": importance,
    }


@router.get("/anomaly-check/{process_line}")
async def check_anomaly(process_line: str):
    """Run anomaly detection on the current snapshot."""
    client    = get_mqtt_client()
    snapshot  = client.get_latest_readings()
    flat_snap = {}
    for k, v in snapshot.items():
        if not k.startswith(f"{process_line}:"):
            continue
        sensor = k.split(":")[1]
        if isinstance(v, dict):
            flat_snap[sensor] = float(v.get("value", 0))
        elif isinstance(v, (int, float)):
            flat_snap[sensor] = float(v)

    detector    = get_anomaly_detector()
    ensemble    = detector.predict(flat_snap)
    per_sensor  = {s: detector.get_sensor_anomaly(s, v) for s, v in flat_snap.items()}

    return {
        "process_line": process_line,
        "ensemble":     ensemble,
        "per_sensor":   per_sensor,
        "sensor_alerts": [
            {"sensor": s, "value": flat_snap[s], **per_sensor[s]}
            for s in per_sensor if per_sensor[s]["is_anomaly"]
        ],
    }


@router.get("/alerts")
async def get_alerts(db: AsyncSession = Depends(get_db)):
    alerts = await get_active_alerts(db)
    return {
        "alerts": [
            {
                "id":          a.id,
                "process_line": a.process_line,
                "sensor_type": a.sensor_type,
                "severity":    a.severity,
                "title":       a.title,
                "description": a.description,
                "ai_recommendation": a.ai_recommendation,
                "timestamp":   a.timestamp.isoformat(),
            }
            for a in alerts
        ],
        "count": len(alerts),
    }


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert_endpoint(alert_id: int, db: AsyncSession = Depends(get_db)):
    alert = await resolve_alert(db, alert_id)
    if not alert:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Alert resolved", "alert_id": alert_id}


@router.get("/dashboard-summary")
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    """Single endpoint returning all data needed for the dashboard."""
    client  = get_mqtt_client()
    latest  = client.get_latest_readings()
    stats   = await get_quality_stats(db, hours=8)
    alerts  = await get_active_alerts(db, limit=5)
    detector = get_anomaly_detector()

    # Anomaly counts per line
    anomaly_per_line = {}
    for line in PROCESS_LINES:
        flat = {}
        for k, v in latest.items():
            if k.startswith(f"{line}:"):
                sensor = k.split(":")[1]
                flat[sensor] = float(v.get("value", 0) if isinstance(v, dict) else v)
        if flat:
            res = detector.predict(flat)
            anomaly_per_line[line] = res.get("is_anomaly", False)
        else:
            anomaly_per_line[line] = False

    normal_lines  = sum(1 for v in anomaly_per_line.values() if not v)
    warning_lines = len(PROCESS_LINES) - normal_lines

    return {
        "kpis": {
            "total_lines":        len(PROCESS_LINES),
            "lines_normal":       normal_lines,
            "lines_warning":      warning_lines,
            "active_alerts":      len(alerts),
            "avg_quality_score":  stats["avg_quality_score"],
            "avg_defect_rate":    round(stats["avg_defect_rate"] * 100, 3),
        },
        "latest_readings": latest,
        "alerts": [
            {"id": a.id, "severity": a.severity, "title": a.title,
             "process_line": a.process_line, "timestamp": a.timestamp.isoformat()}
            for a in alerts
        ],
        "line_status": anomaly_per_line,
    }
