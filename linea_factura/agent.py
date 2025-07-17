import logging
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from data import MODEL_GEMINI_2_5_FLASH
from linea_factura.prompt import LINEA_FACTURA_AGENT_INSTRUCTION
from linea_factura.tools import LINEA_FACTURA_AGENT_TOOLS

logger = logging.getLogger(__name__)

LineaFacturaAgent = LlmAgent(
    name="LineaFacturaAgent",
    model=MODEL_GEMINI_2_5_FLASH,
    description="Agente especializado en gestión, análisis y procesamiento de facturas y documentos financieros",
    instruction=LINEA_FACTURA_AGENT_INSTRUCTION,
    generate_content_config=GenerateContentConfig(
        temperature=0.2,
        max_output_tokens=2500
    ),
    tools=[
        *LINEA_FACTURA_AGENT_TOOLS
    ]
)
