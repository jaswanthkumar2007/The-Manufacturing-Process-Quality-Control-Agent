"""
Report Agent — synthesises all agent outputs into a final response.
"""
import logging
from granite.client import get_granite_client

logger = logging.getLogger(__name__)

REPORT_SYSTEM = """You are a senior manufacturing quality control manager.
Synthesise the analysis from the anomaly detection and knowledge retrieval agents
into a clear, actionable QC report. Structure your response with:
- **Status**: Overall quality status (Normal / Warning / Critical)
- **Key Findings**: Bullet points of main findings
- **Recommendations**: Numbered list of prioritised actions
- **Next Steps**: Immediate actions required
Keep it professional and concise."""


class ReportAgent:
    def __init__(self):
        self.granite = get_granite_client()

    def run(self, state: dict) -> dict:
        prompt = self._build_report_prompt(state)
        response = self.granite.generate(prompt, system_prompt=REPORT_SYSTEM)
        state["final_response"] = response
        return state

    def _build_report_prompt(self, state: dict) -> str:
        sections = []

        sections.append(f"User query: {state.get('user_message', '')}")
        sections.append(f"Process line: {state.get('process_line', 'Unknown')}")

        anomaly = state.get("anomaly_result", {})
        if anomaly.get("is_anomaly"):
            alerts = anomaly.get("sensor_alerts", [])
            alert_str = "; ".join(
                f"{a['sensor']}={a['value']}" for a in alerts
            )
            sections.append(f"Anomaly detected: YES — Sensors: {alert_str}")
            if anomaly.get("interpretation"):
                sections.append(f"Anomaly analysis:\n{anomaly['interpretation']}")
        else:
            sections.append("Anomaly detected: NO — All sensors within normal range")

        rag = state.get("rag_context", {})
        if rag.get("answer"):
            sections.append(f"Knowledge base answer:\n{rag['answer']}")

        snapshot = state.get("sensor_snapshot", {})
        if snapshot:
            snap_str = ", ".join(
                f"{k}={v['value'] if isinstance(v, dict) else v}"
                for k, v in list(snapshot.items())[:6]
            )
            sections.append(f"Current readings: {snap_str}")

        sections.append("Generate a comprehensive QC report based on the above.")

        return "\n\n".join(sections)

    def generate_shift_report(
        self,
        process_line: str,
        quality_stats: dict,
        alert_count: int,
        anomaly_count: int,
    ) -> str:
        prompt = (
            f"Generate a manufacturing shift report for {process_line}.\n\n"
            f"Statistics (last 8 hours):\n"
            f"  - Quality records analysed: {quality_stats.get('total_records', 0)}\n"
            f"  - Average quality score: {quality_stats.get('avg_quality_score', 0):.1f}/100\n"
            f"  - Average defect rate: {quality_stats.get('avg_defect_rate', 0)*100:.2f}%\n"
            f"  - Total defects: {quality_stats.get('total_defects', 0)}\n"
            f"  - Active alerts: {alert_count}\n"
            f"  - Anomalies detected: {anomaly_count}\n\n"
            "Provide a shift summary with status, findings, and recommendations."
        )
        return self.granite.generate(prompt, system_prompt=REPORT_SYSTEM)


_report_agent = None


def get_report_agent():
    global _report_agent
    if _report_agent is None:
        _report_agent = ReportAgent()
    return _report_agent
