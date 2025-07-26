import logging
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from data import MODEL_GEMINI_2_5_FLASH
from .prompt import AGENT_INSTRUCTION
from .tools import AGENT_TOOLS

logger = logging.getLogger(__name__)

FabricantesAgent = LlmAgent(
    name="FabricantesAgent",
    model=MODEL_GEMINI_2_5_FLASH,
    description="Agente especializado en gestión de fabricantes y de los productos que ofrecen.",
    instruction= AGENT_INSTRUCTION,
    generate_content_config=GenerateContentConfig(
        temperature=0.3,
        max_output_tokens=2500
    ),
    tools=[
        *AGENT_TOOLS,
    ]
)
