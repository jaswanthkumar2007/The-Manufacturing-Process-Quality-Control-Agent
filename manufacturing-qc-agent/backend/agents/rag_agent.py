"""
RAG Agent — retrieves manufacturing knowledge and enriches the context.
"""
import logging
from rag.retriever import get_retriever
from granite.client import get_granite_client

logger = logging.getLogger(__name__)

RAG_SYSTEM = """You are a manufacturing knowledge expert with deep expertise in
ISO 9001, SPC, FMEA, and industrial process control. Use the provided context
to give accurate, standards-based answers. Always cite the relevant standard or
methodology. If information is not in the context, say so clearly."""


class RAGAgent:
    def __init__(self):
        self.retriever = get_retriever()
        self.granite   = get_granite_client()

    def run(self, state: dict) -> dict:
        query = self._build_query(state)
        rag_result = self.retriever.answer(query)

        # Augment with Granite if we have context
        if rag_result["has_context"]:
            answer = self.granite.generate(
                rag_result["augmented_prompt"],
                system_prompt=RAG_SYSTEM,
            )
        else:
            answer = self.granite.generate(query, system_prompt=RAG_SYSTEM)

        state["rag_context"] = {
            "query":   query,
            "answer":  answer,
            "sources": rag_result["sources"],
        }
        return state

    def _build_query(self, state: dict) -> str:
        """Build a focused retrieval query from the agent state."""
        msg       = state.get("user_message", "")
        anomalies = state.get("anomaly_result", {}).get("sensor_alerts", [])

        if anomalies:
            sensor_names = [a["sensor"] for a in anomalies]
            return f"{msg} {' '.join(sensor_names)} anomaly root cause corrective action"
        return msg

    def answer_question(self, question: str) -> dict:
        """Standalone RAG Q&A (used by the knowledge-base API endpoint)."""
        rag_result = self.retriever.answer(question)
        if rag_result["has_context"]:
            answer = self.granite.generate(
                rag_result["augmented_prompt"],
                system_prompt=RAG_SYSTEM,
            )
        else:
            answer = self.granite.generate(question, system_prompt=RAG_SYSTEM)
        return {"answer": answer, "sources": rag_result["sources"]}


_rag_agent = None


def get_rag_agent():
    global _rag_agent
    if _rag_agent is None:
        _rag_agent = RAGAgent()
    return _rag_agent
