import logging
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from data import MODEL_GEMINI_2_0_FLASH
from familia.prompt import FAMILIA_AGENT_INSTRUCTION
from familia.tools import FAMILIA_AGENT_TOOLS
from components import ExitLoopSignalTool

logger = logging.getLogger(__name__)

FamiliaAgent = LlmAgent(
    name="FamiliaAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Agente especializado en identificación de familias de productos. Este agente puede identificar familias de productos y proporcionar información relevante sobre ellas.",
    instruction=FAMILIA_AGENT_INSTRUCTION,
    generate_content_config=GenerateContentConfig(
        temperature=0.3,
        max_output_tokens=2500
    ),    
    tools=[
        *FAMILIA_AGENT_TOOLS,
        ExitLoopSignalTool
    ]
)

