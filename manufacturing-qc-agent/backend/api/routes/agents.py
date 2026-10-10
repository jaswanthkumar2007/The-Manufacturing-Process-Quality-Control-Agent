"""
Agent chat API routes.
"""
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from db.database import get_db
from db.crud import save_message, get_conversation_history
from agents.orchestrator import run_agent
from mqtt.client import get_mqtt_client
from ml.quality_predictor import get_quality_predictor
from ml.anomaly_detector import get_anomaly_detector

router = APIRouter(prefix="/agents", tags=["Agents"])


class ChatRequest(BaseModel):
    session_id:   Optional[str] = None
    message:      str
    process_line: Optional[str] = "CNC_LINE_A"


class ChatResponse(BaseModel):
    session_id:     str
    response:       str
    agent_route:    str
    anomaly_result: dict
    rag_sources:    list
    quality_result: dict


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    session_id = req.session_id or str(uuid.uuid4())

    # Load history
    history_records = await get_conversation_history(db, session_id, limit=10)
    history = [{"role": r.role, "content": r.content} for r in history_records]

    # Get latest sensor snapshot
    client   = get_mqtt_client()
    snapshot = client.get_latest_readings()
    line_snapshot = {
        k.split(":")[1]: v for k, v in snapshot.items()
        if k.startswith(f"{req.process_line}:")
    }

    # Quality prediction on snapshot
    predictor = get_quality_predictor()
    flat_snap = {}
    for k, v in line_snapshot.items():
        if isinstance(v, dict):
            flat_snap[k] = float(v.get("value", 0))
        elif isinstance(v, (int, float)):
            flat_snap[k] = float(v)
    quality_result = predictor.predict(flat_snap) if flat_snap else {}

    # Save user message
    await save_message(db, session_id, "user", req.message, "qc_agent")

    # Run agent graph
    result = await run_agent(
        session_id=session_id,
        user_message=req.message,
        sensor_snapshot=line_snapshot,
        process_line=req.process_line,
        history=history,
    )

    # Save assistant response
    await save_message(db, session_id, "assistant", result["response"], "qc_agent")

    return ChatResponse(
        session_id=session_id,
        response=result["response"],
        agent_route=result.get("route", ""),
        anomaly_result=result.get("anomaly_result", {}),
        rag_sources=result.get("rag_sources", []),
        quality_result=quality_result,
    )


@router.get("/history/{session_id}")
async def get_history(session_id: str, db: AsyncSession = Depends(get_db)):
    records = await get_conversation_history(db, session_id, limit=50)
    return {
        "session_id": session_id,
        "messages": [
            {"role": r.role, "content": r.content, "timestamp": r.timestamp.isoformat()}
            for r in records
        ],
    }


@router.get("/status")
async def get_agent_status():
    """Return current status of all agents and ML models."""
    from granite.client import get_granite_client
    granite = get_granite_client()
    return {
        "agents": [
            {"name": "QC Agent",      "type": "orchestrator", "status": "active"},
            {"name": "Anomaly Agent", "type": "ml+llm",       "status": "active"},
            {"name": "RAG Agent",     "type": "rag+llm",      "status": "active"},
            {"name": "Report Agent",  "type": "llm",          "status": "active"},
        ],
        "granite": {
            "model":    "ibm/granite-13b-instruct-v2",
            "mock_mode": granite._mock_mode,
            "platform":  "IBM watsonx.ai",
        },
    }
