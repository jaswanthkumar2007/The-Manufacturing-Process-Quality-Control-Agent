# Manufacturing Process Quality Control Agent

A full-stack AI-powered manufacturing quality control system using IBM Granite, watsonx.ai, LangGraph multi-agent orchestration, RAG, and real-time MQTT sensor integration.

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React.js 18, HTML, CSS, JavaScript |
| **UI Styling** | Tailwind CSS |
| **Backend** | Python 3.11, FastAPI |
| **AI / LLM** | IBM Granite Models |
| **AI Platform** | IBM watsonx.ai |
| **AI Development** | IBM Bob |
| **Multi-Agent** | LangGraph + custom Python agents |
| **Machine Learning** | Scikit-learn |
| **RAG** | LangChain + ChromaDB |
| **Vector Database** | ChromaDB |
| **Database** | PostgreSQL |
| **Real-Time** | MQTT, WebSockets |
| **Visualization** | Recharts |
| **Cloud** | IBM Cloud |
| **Version Control** | Git & GitHub |

## Architecture

```
manufacturing-qc-agent/
├── backend/
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # All configuration / env vars
│   ├── requirements.txt
│   ├── agents/
│   │   ├── orchestrator.py        # LangGraph multi-agent graph
│   │   ├── qc_agent.py            # Quality Control agent
│   │   ├── anomaly_agent.py       # Anomaly detection agent
│   │   ├── rag_agent.py           # RAG knowledge agent
│   │   └── report_agent.py        # Report generation agent
│   ├── api/
│   │   ├── routes/
│   │   │   ├── sensors.py         # Sensor data endpoints
│   │   │   ├── analysis.py        # QC analysis endpoints
│   │   │   ├── agents.py          # Agent chat endpoints
│   │   │   ├── reports.py         # Report endpoints
│   │   │   └── knowledge.py       # RAG knowledge endpoints
│   │   └── websocket.py           # WebSocket manager
│   ├── ml/
│   │   ├── anomaly_detector.py    # IsolationForest / One-class SVM
│   │   ├── quality_predictor.py   # RandomForest quality classifier
│   │   └── data_processor.py      # Pandas feature engineering
│   ├── rag/
│   │   ├── vector_store.py        # ChromaDB operations
│   │   ├── knowledge_base.py      # Manufacturing knowledge docs
│   │   └── retriever.py           # RAG retrieval pipeline
│   ├── mqtt/
│   │   ├── client.py              # MQTT subscriber/publisher
│   │   └── simulator.py           # Sensor data simulator
│   ├── db/
│   │   ├── database.py            # PostgreSQL SQLAlchemy setup
│   │   ├── models.py              # ORM models
│   │   └── crud.py                # Database operations
│   └── granite/
│       └── client.py              # IBM watsonx.ai Granite client
└── frontend/
    ├── package.json
    ├── tailwind.config.js
    ├── public/index.html
    └── src/
        ├── App.jsx
        ├── index.css
        ├── api/
        │   └── client.js
        ├── components/
        │   ├── Layout/Sidebar.jsx
        │   ├── Layout/Header.jsx
        │   ├── Charts/SensorChart.jsx
        │   ├── Charts/ControlChart.jsx
        │   ├── Charts/AnomalyChart.jsx
        │   ├── Charts/QualityGauge.jsx
        │   └── UI/StatusBadge.jsx
        ├── hooks/
        │   ├── useWebSocket.js
        │   └── useSensorData.js
        └── pages/
            ├── Dashboard.jsx
            ├── LiveMonitor.jsx
            ├── QCAnalysis.jsx
            ├── AgentConsole.jsx
            └── KnowledgeBase.jsx
```

## Getting Started

### Prerequisites
- Python 3.11+, Node.js 18+
- PostgreSQL 15+, Docker (optional)
- IBM Cloud account with watsonx.ai access
- MQTT broker (Mosquitto recommended)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # Fill in IBM credentials
uvicorn main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm start                     # http://localhost:3000
```

### Environment Variables (.env)
```
WATSONX_API_KEY=your_ibm_api_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
GRANITE_MODEL_ID=ibm/granite-13b-instruct-v2
DATABASE_URL=postgresql://user:pass@localhost:5432/manufacturing_qc
MQTT_BROKER=localhost
MQTT_PORT=1883
SECRET_KEY=your_secret_key
```
