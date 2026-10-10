"""
Reports API routes.
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from db.database import get_db
from db.crud import create_report, get_reports, get_quality_stats, get_active_alerts
from agents.report_agent import get_report_agent

router = APIRouter(prefix="/reports", tags=["Reports"])


class ReportRequest(BaseModel):
    process_line: str = "CNC_LINE_A"
    period_hours: int = 8


@router.post("/generate")
async def generate_report(req: ReportRequest, db: AsyncSession = Depends(get_db)):
    """Generate an AI-powered shift report."""
    stats       = await get_quality_stats(db, hours=req.period_hours)
    alerts      = await get_active_alerts(db, limit=100)

    report_agent = get_report_agent()
    summary = report_agent.generate_shift_report(
        process_line=req.process_line,
        quality_stats=stats,
        alert_count=len(alerts),
        anomaly_count=sum(1 for a in alerts if a.severity in ("high", "critical")),
    )

    from datetime import timedelta
    now = datetime.utcnow()
    report = await create_report(db, {
        "report_id":          str(uuid.uuid4())[:8].upper(),
        "process_line":       req.process_line,
        "period_start":       now - timedelta(hours=req.period_hours),
        "period_end":         now,
        "summary":            summary,
        "recommendations":    "",
        "total_alerts":       len(alerts),
        "avg_quality_score":  stats["avg_quality_score"],
        "generated_by":       "ai_agent",
    })

    return {
        "report_id":    report.report_id,
        "process_line": report.process_line,
        "summary":      report.summary,
        "period_hours": req.period_hours,
        "generated_at": report.timestamp.isoformat(),
    }


@router.get("/")
async def list_reports(
    limit: int = Query(10, le=50),
    db: AsyncSession = Depends(get_db),
):
    reports = await get_reports(db, limit)
    return {
        "reports": [
            {
                "report_id":    r.report_id,
                "process_line": r.process_line,
                "summary":      r.summary[:200] + "...",
                "total_alerts": r.total_alerts,
                "avg_quality":  r.avg_quality_score,
                "timestamp":    r.timestamp.isoformat(),
            }
            for r in reports
        ]
    }
