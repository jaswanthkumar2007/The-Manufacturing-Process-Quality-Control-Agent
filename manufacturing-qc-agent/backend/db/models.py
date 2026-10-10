"""
SQLAlchemy ORM models for the Manufacturing QC Agent.
"""
from datetime import datetime
from sqlalchemy import (
    String, Float, Integer, Boolean, Text, DateTime,
    ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.database import Base
import enum


class QualityStatus(str, enum.Enum):
    pass_  = "pass"
    fail   = "fail"
    review = "review"
    unknown = "unknown"


class AlertSeverity(str, enum.Enum):
    low      = "low"
    medium   = "medium"
    high     = "high"
    critical = "critical"


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id:          Mapped[int]      = mapped_column(Integer, primary_key=True, index=True)
    sensor_id:   Mapped[str]      = mapped_column(String(64), index=True)
    sensor_type: Mapped[str]      = mapped_column(String(64))
    process_line:Mapped[str]      = mapped_column(String(64), index=True)
    value:       Mapped[float]    = mapped_column(Float)
    unit:        Mapped[str]      = mapped_column(String(16))
    is_anomaly:  Mapped[bool]     = mapped_column(Boolean, default=False)
    anomaly_score: Mapped[float]  = mapped_column(Float, default=0.0)
    timestamp:   Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    alerts: Mapped[list["Alert"]] = relationship(back_populates="reading")


class QualityRecord(Base):
    __tablename__ = "quality_records"

    id:           Mapped[int]    = mapped_column(Integer, primary_key=True, index=True)
    process_line: Mapped[str]    = mapped_column(String(64), index=True)
    batch_id:     Mapped[str]    = mapped_column(String(64), index=True)
    quality_score:Mapped[float]  = mapped_column(Float)
    status:       Mapped[str]    = mapped_column(String(16), default="unknown")
    defect_count: Mapped[int]    = mapped_column(Integer, default=0)
    total_units:  Mapped[int]    = mapped_column(Integer, default=0)
    defect_rate:  Mapped[float]  = mapped_column(Float, default=0.0)
    notes:        Mapped[str]    = mapped_column(Text, default="")
    timestamp:    Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class Alert(Base):
    __tablename__ = "alerts"

    id:           Mapped[int]    = mapped_column(Integer, primary_key=True, index=True)
    reading_id:   Mapped[int]    = mapped_column(Integer, ForeignKey("sensor_readings.id"), nullable=True)
    process_line: Mapped[str]    = mapped_column(String(64))
    sensor_type:  Mapped[str]    = mapped_column(String(64))
    severity:     Mapped[str]    = mapped_column(String(16))
    title:        Mapped[str]    = mapped_column(String(256))
    description:  Mapped[str]    = mapped_column(Text)
    ai_recommendation: Mapped[str] = mapped_column(Text, default="")
    is_resolved:  Mapped[bool]   = mapped_column(Boolean, default=False)
    resolved_at:  Mapped[datetime] = mapped_column(DateTime, nullable=True)
    timestamp:    Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    reading: Mapped["SensorReading"] = relationship(back_populates="alerts")


class AgentConversation(Base):
    __tablename__ = "agent_conversations"

    id:        Mapped[int]    = mapped_column(Integer, primary_key=True, index=True)
    session_id:Mapped[str]    = mapped_column(String(64), index=True)
    role:      Mapped[str]    = mapped_column(String(16))      # user | assistant
    content:   Mapped[str]    = mapped_column(Text)
    agent_name:Mapped[str]    = mapped_column(String(64), default="qc_agent")
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ProcessReport(Base):
    __tablename__ = "process_reports"

    id:           Mapped[int]    = mapped_column(Integer, primary_key=True, index=True)
    report_id:    Mapped[str]    = mapped_column(String(64), unique=True, index=True)
    process_line: Mapped[str]    = mapped_column(String(64))
    period_start: Mapped[datetime] = mapped_column(DateTime)
    period_end:   Mapped[datetime] = mapped_column(DateTime)
    summary:      Mapped[str]    = mapped_column(Text)
    recommendations: Mapped[str] = mapped_column(Text)
    total_alerts: Mapped[int]    = mapped_column(Integer, default=0)
    avg_quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    generated_by: Mapped[str]    = mapped_column(String(64), default="ai_agent")
    timestamp:    Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
