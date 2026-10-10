"""
LangGraph multi-agent orchestration for the Manufacturing QC system.

Graph topology:
  [user_input]
       ↓
  [qc_agent]  ─── routes ──→  [anomaly_agent]
       │                           ↓
       │                      [rag_agent]
       │                           ↓
       └──────────────────── [report_agent]
                                   ↓
                             [__end__]
"""
import logging
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END

from agents.qc_agent     import QCAgent
from agents.anomaly_agent import AnomalyAgent
from agents.rag_agent    import RAGAgent
from agents.report_agent import ReportAgent

logger = logging.getLogger(__name__)


# ── Shared Graph State ────────────────────────────────────────────────────────

class AgentState(TypedDict):
    session_id:      str
    user_message:    str
    sensor_snapshot: dict          # Latest readings
    process_line:    str
    anomaly_result:  dict
    rag_context:     dict
    qc_analysis:     str
    final_response:  str
    route:           str           # Which branch to take
    history:         list[dict]


# ── Nodes ─────────────────────────────────────────────────────────────────────

qc_agent_node     = QCAgent()
anomaly_agent_node = AnomalyAgent()
rag_agent_node    = RAGAgent()
report_agent_node = ReportAgent()


def qc_node(state: AgentState) -> AgentState:
    return qc_agent_node.run(state)


def anomaly_node(state: AgentState) -> AgentState:
    return anomaly_agent_node.run(state)


def rag_node(state: AgentState) -> AgentState:
    return rag_agent_node.run(state)


def report_node(state: AgentState) -> AgentState:
    return report_agent_node.run(state)


# ── Routing ───────────────────────────────────────────────────────────────────

def route_after_qc(state: AgentState) -> Literal["anomaly", "rag", "report", "__end__"]:
    """Decide which sub-agent handles the query."""
    route = state.get("route", "report")
    if route in ("anomaly", "rag", "report"):
        return route
    return "report"


# ── Build Graph ───────────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("qc_agent",     qc_node)
    graph.add_node("anomaly_agent", anomaly_node)
    graph.add_node("rag_agent",    rag_node)
    graph.add_node("report_agent", report_node)

    graph.set_entry_point("qc_agent")

    graph.add_conditional_edges(
        "qc_agent",
        route_after_qc,
        {
            "anomaly": "anomaly_agent",
            "rag":     "rag_agent",
            "report":  "report_agent",
        },
    )

    # After anomaly → pass to rag for context enrichment → then report
    graph.add_edge("anomaly_agent", "rag_agent")
    graph.add_edge("rag_agent",     "report_agent")
    graph.add_edge("report_agent",  END)

    return graph.compile()


# Singleton
_graph = None


def get_agent_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
        logger.info("LangGraph multi-agent graph compiled")
    return _graph


async def run_agent(
    session_id: str,
    user_message: str,
    sensor_snapshot: dict,
    process_line: str,
    history: list[dict],
) -> dict:
    """
    Execute the full agent graph for one user turn.
    Returns the final state including response text.
    """
    graph = get_agent_graph()

    initial_state: AgentState = {
        "session_id":      session_id,
        "user_message":    user_message,
        "sensor_snapshot": sensor_snapshot,
        "process_line":    process_line,
        "anomaly_result":  {},
        "rag_context":     {},
        "qc_analysis":     "",
        "final_response":  "",
        "route":           "report",
        "history":         history,
    }

    try:
        final_state = graph.invoke(initial_state)
        return {
            "response":       final_state.get("final_response", ""),
            "anomaly_result": final_state.get("anomaly_result", {}),
            "rag_sources":    final_state.get("rag_context", {}).get("sources", []),
            "route":          final_state.get("route", ""),
        }
    except Exception as exc:
        logger.error("Agent graph execution error: %s", exc)
        return {
            "response": f"⚠️ Agent error: {exc}. Please check configuration.",
            "anomaly_result": {},
            "rag_sources": [],
            "route": "error",
        }
