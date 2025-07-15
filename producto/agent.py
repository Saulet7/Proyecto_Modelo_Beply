import logging
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from data import MODEL_GEMINI_2_0_FLASH
from producto.prompt import PRODUCTO_AGENT_INSTRUCTION
from producto.tools import PRODUCTO_AGENT_TOOLS
from components import ExitLoopSignalTool

logger = logging.getLogger(__name__)

ProductoAgent = LlmAgent(
    name="ProductoAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Agente especializado en gestión de productos y catálogo",
    instruction=PRODUCTO_AGENT_INSTRUCTION,
    generate_content_config=GenerateContentConfig(
        temperature=0.2,
        max_output_tokens=2500
    ),
    tools=[
        *PRODUCTO_AGENT_TOOLS,
        ExitLoopSignalTool
    ]
)