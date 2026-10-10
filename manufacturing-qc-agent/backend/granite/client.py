"""
IBM watsonx.ai Granite client.
Falls back to mock responses gracefully when credentials are not configured.
"""
import logging
from typing import Optional
from config import get_settings

logger = logging.getLogger(__name__)


class GraniteClient:
    """Wraps IBM watsonx.ai Granite model inference."""

    def __init__(self):
        self.settings = get_settings()
        self.model = None
        self._initialized = False
        self._mock_mode = False
        self._try_init()

    def _try_init(self):
        """Attempt to initialise the real watsonx.ai client."""
        if not self.settings.watsonx_api_key or not self.settings.watsonx_project_id:
            logger.warning(
                "WATSONX_API_KEY or WATSONX_PROJECT_ID not set — "
                "running in mock mode. Set env vars for real IBM Granite responses."
            )
            self._mock_mode = True
            return

        try:
            from ibm_watsonx_ai import Credentials
            from ibm_watsonx_ai.foundation_models import ModelInference
            from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

            creds = Credentials(
                url=self.settings.watsonx_url,
                api_key=self.settings.watsonx_api_key,
            )

            params = {
                GenParams.MAX_NEW_TOKENS: self.settings.granite_max_tokens,
                GenParams.TEMPERATURE:    self.settings.granite_temperature,
                GenParams.TOP_P:          self.settings.granite_top_p,
                GenParams.STOP_SEQUENCES: ["</s>", "\n\nHuman:", "\n\nUser:"],
            }

            self.model = ModelInference(
                model_id=self.settings.granite_model_id,
                credentials=creds,
                project_id=self.settings.watsonx_project_id,
                params=params,
            )
            self._initialized = True
            logger.info(
                "IBM Granite client initialised — model: %s",
                self.settings.granite_model_id,
            )
        except ImportError:
            logger.error("ibm-watsonx-ai package not installed — falling back to mock mode.")
            self._mock_mode = True
        except Exception as exc:
            logger.error("Failed to initialise watsonx.ai client: %s — mock mode", exc)
            self._mock_mode = True

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a response from IBM Granite."""
        if self._mock_mode:
            return self._mock_response(prompt)

        full_prompt = self._build_prompt(prompt, system_prompt)
        try:
            response = self.model.generate_text(prompt=full_prompt)
            return response.strip()
        except Exception as exc:
            logger.error("Granite inference error: %s", exc)
            return self._mock_response(prompt)

    def _build_prompt(self, user_msg: str, system_prompt: Optional[str]) -> str:
        """Format prompt for IBM Granite instruct models."""
        sys = system_prompt or (
            "You are an expert manufacturing quality control engineer. "
            "You analyse sensor data, detect anomalies, and provide actionable "
            "recommendations based on ISO 9001, SPC principles, and FMEA methodology. "
            "Be concise, technical, and precise."
        )
        return (
            f"<|system|>\n{sys}\n<|user|>\n{user_msg}\n<|assistant|>\n"
        )

    def _mock_response(self, prompt: str) -> str:
        """Return a realistic mock response for demo/dev mode."""
        p = prompt.lower()
        if "anomaly" in p or "alert" in p:
            return (
                "⚠️ **Anomaly Detected** (Mock Mode)\n\n"
                "Based on the sensor readings, an anomaly has been identified in the "
                "temperature sensor on CNC_LINE_A. The reading of 89.3°C exceeds the "
                "Upper Control Limit (UCL) of 80°C.\n\n"
                "**Recommended Actions:**\n"
                "1. Inspect cooling system for blockages\n"
                "2. Verify coolant flow rate — check SENSOR flow_rate\n"
                "3. Reduce spindle speed by 15% as a precautionary measure\n"
                "4. Schedule preventive maintenance within 4 hours\n\n"
                "*Note: IBM Granite credentials not configured — running in mock mode.*"
            )
        if "quality" in p or "predict" in p:
            return (
                "📊 **Quality Prediction Report** (Mock Mode)\n\n"
                "Current process parameters indicate a **PASS** outcome with 87% confidence.\n\n"
                "| Parameter | Value | Status |\n"
                "|-----------|-------|--------|\n"
                "| Temperature | 72.4°C | ✅ Normal |\n"
                "| Pressure | 6.8 bar | ✅ Normal |\n"
                "| Vibration | 1.2 mm/s | ✅ Normal |\n\n"
                "Process is within Statistical Process Control limits."
            )
        if "report" in p or "summary" in p:
            return (
                "📋 **QC Shift Summary Report** (Mock Mode)\n\n"
                "**Period:** Last 8 hours | **Line:** CNC_LINE_A\n\n"
                "- Total units produced: 1,247\n"
                "- Defect rate: 1.8% (target: <3%)\n"
                "- Anomalies detected: 3\n"
                "- SPC violations: 1 (Rule 1 — point beyond 3σ)\n\n"
                "**Overall Status: ✅ ACCEPTABLE**"
            )
        return (
            "I am the Manufacturing QC Agent powered by IBM Granite. "
            "I can help you analyse sensor data, detect anomalies, predict quality outcomes, "
            "and retrieve knowledge from the manufacturing knowledge base.\n\n"
            "*Note: IBM Granite credentials not configured — running in mock mode.*"
        )


# Singleton
_client: Optional[GraniteClient] = None


def get_granite_client() -> GraniteClient:
    global _client
    if _client is None:
        _client = GraniteClient()
    return _client
