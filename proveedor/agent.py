import logging
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from data import MODEL_GEMINI_2_0_FLASH
from proveedor.prompt import PROVEEDOR_AGENT_INSTRUCTION
from proveedor.tools import PROVEEDOR_AGENT_TOOLS
from components import ExitLoopSignalTool

logger = logging.getLogger(__name__)

ProveedorAgent = LlmAgent(
    name="ProveedorAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Agente especializado en identificación, análisis y documentación de supuestos en procesos empresariales por parte de los proveedores",
    instruction=PROVEEDOR_AGENT_INSTRUCTION,
    generate_content_config=GenerateContentConfig(
        temperature=0.3,
        max_output_tokens=2500
    ),    
    tools=[
        *PROVEEDOR_AGENT_TOOLS,
        ExitLoopSignalTool
    ]
)

