"""
QC Agent — primary orchestrator node.
Understands the user intent and routes to the appropriate sub-agent.
"""
import logging
from granite.client import get_granite_client

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert AI Manufacturing Quality Control Engineer.
You monitor real-time sensor data from production lines and help diagnose quality issues.
You follow ISO 9001, SPC, and FMEA principles.

Your capabilities:
1. Anomaly detection and root-cause analysis
2. Quality prediction and trend analysis
3. Knowledge retrieval (ISO standards, defect catalogs, SPC rules)
4. Generating shift reports and corrective action recommendations

When responding:
- Be concise and technical
- Provide specific actionable recommendations
- Reference SPC rules, ISO clauses, or FMEA categories when relevant
- Use metric units
"""

INTENT_KEYWORDS = {
    "anomaly":  ["anomaly", "alert", "spike", "outlier", "deviation", "fault", "failure", "error", "alarm"],
    "rag":      ["what is", "explain", "how to", "standard", "iso", "fmea", "spc", "definition", "guide"],
    "report":   ["report", "summary", "status", "overview", "shift", "performance", "kpi", "oee"],
}


class QCAgent:
    def __init__(self):
        self.granite = get_granite_client()

    def run(self, state: dict) -> dict:
        msg = state["user_message"].lower()
        route = self._detect_intent(msg)
        state["route"] = route
        logger.debug("QCAgent routed '%s' → %s", msg[:40], route)
        return state

    def _detect_intent(self, message: str) -> str:
        for intent, keywords in INTENT_KEYWORDS.items():
            if any(k in message for k in keywords):
                return intent
        return "report"

    def generate_analysis(self, message: str, sensor_snapshot: dict) -> str:
        snapshot_str = "\n".join(
            f"  {k}: {v['value']} {v['unit']}" if isinstance(v, dict) else f"  {k}: {v}"
            for k, v in sensor_snapshot.items()
        )
        prompt = (
            f"Current sensor readings:\n{snapshot_str}\n\n"
            f"User query: {message}\n\n"
            "Provide a quality control analysis."
        )
        return self.granite.generate(prompt, system_prompt=SYSTEM_PROMPT)
