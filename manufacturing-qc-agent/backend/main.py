"""
FastAPI main application entry point.
Registers all routes, WebSocket, MQTT, and startup/shutdown hooks.
"""
import asyncio
import json
import logging
import sys
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from db.database import init_db
from api.websocket import manager
from api.routes.sensors  import router as sensors_router
from api.routes.analysis import router as analysis_router
from api.routes.agents   import router as agents_router
from api.routes.reports  import router as reports_router
from api.routes.knowledge import router as knowledge_router

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)
settings = get_settings()

# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    logger.info("🚀 Starting Manufacturing QC Agent backend...")

    # 1. Initialise DB
    try:
        await init_db()
        logger.info("✅ PostgreSQL database initialised")
    except Exception as exc:
        logger.warning("⚠️  DB init failed (running without persistence): %s", exc)

    # 2. Start MQTT / Simulator
    try:
        from mqtt.client import get_mqtt_client
        mqtt_client = get_mqtt_client()

        def on_sensor_message(topic: str, payload: dict):
            """Forward MQTT messages to all WebSocket clients."""
            asyncio.run_coroutine_threadsafe(
                manager.broadcast({
                    "type":    "sensor_reading",
                    "topic":   topic,
                    "payload": payload,
                }),
                asyncio.get_event_loop(),
            )
        mqtt_client.subscribe(on_sensor_message)
        logger.info("✅ MQTT/Simulator started")
    except Exception as exc:
        logger.warning("⚠️  MQTT init failed: %s", exc)

    # 3. Pre-warm ML models
    try:
        from ml.anomaly_detector import get_anomaly_detector
        from ml.quality_predictor import get_quality_predictor
        get_anomaly_detector()
        get_quality_predictor()
        logger.info("✅ ML models ready")
    except Exception as exc:
        logger.warning("⚠️  ML model init failed: %s", exc)

    # 4. Pre-warm RAG / ChromaDB
    try:
        from rag.vector_store import get_vector_store
        vs = get_vector_store()
        logger.info("✅ ChromaDB vector store ready (%d docs)", vs.count)
    except Exception as exc:
        logger.warning("⚠️  ChromaDB init failed: %s", exc)

    # 5. Granite client
    try:
        from granite.client import get_granite_client
        gc = get_granite_client()
        mode = "mock" if gc._mock_mode else "IBM watsonx.ai"
        logger.info("✅ IBM Granite client ready [mode: %s]", mode)
    except Exception as exc:
        logger.warning("⚠️  Granite init failed: %s", exc)

    logger.info("✅ All services started — API ready at http://0.0.0.0:8000")
    yield

    logger.info("🛑 Shutting down Manufacturing QC Agent...")
    try:
        from mqtt.client import get_mqtt_client
        get_mqtt_client().stop()
    except Exception:
        pass


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Manufacturing QC Agent API",
    description=(
        "AI-powered manufacturing quality control using IBM Granite, "
        "LangGraph multi-agent system, RAG with ChromaDB, "
        "real-time MQTT sensor integration, and Scikit-learn ML."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(sensors_router,  prefix="/api/v1")
app.include_router(analysis_router, prefix="/api/v1")
app.include_router(agents_router,   prefix="/api/v1")
app.include_router(reports_router,  prefix="/api/v1")
app.include_router(knowledge_router, prefix="/api/v1")


# ── WebSocket ─────────────────────────────────────────────────────────────────

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    Real-time WebSocket endpoint.
    Streams: sensor readings, anomaly alerts, quality predictions.
    """
    await manager.connect(websocket, session_id)
    try:
        while True:
            # Keep connection alive; actual data is pushed via broadcast
            data = await websocket.receive_text()
            if data == "ping":
                await manager.send(session_id, {"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as exc:
        logger.error("WebSocket error (%s): %s", session_id, exc)
        manager.disconnect(session_id)


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    return {
        "status":  "healthy",
        "service": "manufacturing-qc-agent",
        "version": "1.0.0",
        "platform": "IBM Cloud / watsonx.ai",
    }


@app.get("/")
async def root():
    return {
        "message": "Manufacturing Process Quality Control Agent",
        "docs":    "/docs",
        "health":  "/health",
    }
