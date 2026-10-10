"""
CRUD operations for the Manufacturing QC database.
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import SensorReading, QualityRecord, Alert, AgentConversation, ProcessReport


# ── Sensor Readings ──────────────────────────────────────────────────────────

async def create_sensor_reading(db: AsyncSession, data: dict) -> SensorReading:
    reading = SensorReading(**data)
    db.add(reading)
    await db.flush()
    await db.refresh(reading)
    return reading


async def get_recent_readings(
    db: AsyncSession, sensor_type: Optional[str] = None,
    process_line: Optional[str] = None, limit: int = 100
) -> list[SensorReading]:
    q = select(SensorReading).order_by(desc(SensorReading.timestamp)).limit(limit)
    if sensor_type:
        q = q.where(SensorReading.sensor_type == sensor_type)
    if process_line:
        q = q.where(SensorReading.process_line == process_line)
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_anomaly_readings(db: AsyncSession, hours: int = 24) -> list[SensorReading]:
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    q = (select(SensorReading)
         .where(SensorReading.is_anomaly == True)
         .where(SensorReading.timestamp >= cutoff)
         .order_by(desc(SensorReading.timestamp)))
    result = await db.execute(q)
    return list(result.scalars().all())


# ── Quality Records ──────────────────────────────────────────────────────────

async def create_quality_record(db: AsyncSession, data: dict) -> QualityRecord:
    record = QualityRecord(**data)
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


async def get_quality_stats(db: AsyncSession, hours: int = 24) -> dict:
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    q = select(
        func.count(QualityRecord.id).label("total"),
        func.avg(QualityRecord.quality_score).label("avg_score"),
        func.avg(QualityRecord.defect_rate).label("avg_defect_rate"),
        func.sum(QualityRecord.defect_count).label("total_defects"),
    ).where(QualityRecord.timestamp >= cutoff)
    result = await db.execute(q)
    row = result.one()
    return {
        "total_records":    row.total or 0,
        "avg_quality_score": round(float(row.avg_score or 0), 2),
        "avg_defect_rate":  round(float(row.avg_defect_rate or 0), 4),
        "total_defects":    row.total_defects or 0,
    }


# ── Alerts ───────────────────────────────────────────────────────────────────

async def create_alert(db: AsyncSession, data: dict) -> Alert:
    alert = Alert(**data)
    db.add(alert)
    await db.flush()
    await db.refresh(alert)
    return alert


async def get_active_alerts(db: AsyncSession, limit: int = 50) -> list[Alert]:
    q = (select(Alert)
         .where(Alert.is_resolved == False)
         .order_by(desc(Alert.timestamp))
         .limit(limit))
    result = await db.execute(q)
    return list(result.scalars().all())


async def resolve_alert(db: AsyncSession, alert_id: int) -> Optional[Alert]:
    q = select(Alert).where(Alert.id == alert_id)
    result = await db.execute(q)
    alert = result.scalar_one_or_none()
    if alert:
        alert.is_resolved = True
        alert.resolved_at = datetime.utcnow()
    return alert


# ── Agent Conversations ──────────────────────────────────────────────────────

async def save_message(db: AsyncSession, session_id: str, role: str,
                        content: str, agent_name: str = "qc_agent") -> AgentConversation:
    msg = AgentConversation(
        session_id=session_id, role=role,
        content=content, agent_name=agent_name
    )
    db.add(msg)
    await db.flush()
    return msg


async def get_conversation_history(
    db: AsyncSession, session_id: str, limit: int = 20
) -> list[AgentConversation]:
    q = (select(AgentConversation)
         .where(AgentConversation.session_id == session_id)
         .order_by(AgentConversation.timestamp)
         .limit(limit))
    result = await db.execute(q)
    return list(result.scalars().all())


# ── Reports ──────────────────────────────────────────────────────────────────

async def create_report(db: AsyncSession, data: dict) -> ProcessReport:
    report = ProcessReport(**data)
    db.add(report)
    await db.flush()
    await db.refresh(report)
    return report


async def get_reports(db: AsyncSession, limit: int = 10) -> list[ProcessReport]:
    q = select(ProcessReport).order_by(desc(ProcessReport.timestamp)).limit(limit)
    result = await db.execute(q)
    return list(result.scalars().all())
