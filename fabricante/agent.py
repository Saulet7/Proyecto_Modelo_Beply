import logging
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from data import MODEL_GEMINI_2_0_FLASH
from fabricante.prompt import FABRICANTE_AGENT_INSTRUCTION
from fabricante.tools import FABRICANTE_AGENT_TOOLS
from components import ExitLoopSignalTool

logger = logging.getLogger(__name__)

FabricanteAgent = LlmAgent(
    name="FabricanteAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Agente especializado en gestión de fabricantes y de los productos que ofrecen.",
    instruction=FABRICANTE_AGENT_INSTRUCTION,
    generate_content_config=GenerateContentConfig(
        temperature=0.3,
        max_output_tokens=2500
    ),
    tools=[
        *FABRICANTE_AGENT_TOOLS,
        ExitLoopSignalTool
    ]
)
