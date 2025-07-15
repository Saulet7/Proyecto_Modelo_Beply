import logging
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from data import MODEL_GEMINI_2_0_FLASH
from factura.prompt import FACTURA_AGENT_INSTRUCTION
from factura.tools import FACTURA_AGENT_TOOLS
from components import ExitLoopSignalTool

logger = logging.getLogger(__name__)

FacturaAgent = LlmAgent(
    name="FacturaAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Agente especializado en gestión, análisis y procesamiento de facturas y documentos financieros",
    instruction=FACTURA_AGENT_INSTRUCTION,
    generate_content_config=GenerateContentConfig(
        temperature=0.2,
        max_output_tokens=2500
    ),
    tools=[
        *FACTURA_AGENT_TOOLS,
        ExitLoopSignalTool  # Herramienta para señalizar salida del bucle actual
    ]
)
