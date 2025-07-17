import logging
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from data import MODEL_GEMINI_2_5_FLASH
from creador_factura.prompt import FACTURA_AGENT_INSTRUCTION
from creador_factura.tools import FACTURA_AGENT_TOOLS

logger = logging.getLogger(__name__)

CreadorFacturaAgent = LlmAgent(
    name="CreadorFacturaAgent",
    model=MODEL_GEMINI_2_5_FLASH,
    description="Agente especializado en la creación de facturas.",
    instruction=FACTURA_AGENT_INSTRUCTION,
    generate_content_config=GenerateContentConfig(
        temperature=0.2,
        max_output_tokens=2500
    ),
    tools=[
        *FACTURA_AGENT_TOOLS
    ]
)
