import logging
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from data import MODEL_GEMINI_2_5_FLASH
from .prompt import AGENT_INSTRUCTION
from .tools import AGENT_TOOLS

logger = logging.getLogger(__name__)

FamiliasAgent = LlmAgent(
    name="FamiliasAgent",
    model=MODEL_GEMINI_2_5_FLASH,
    description="Agente especializado en identificación de familias de productos. Este agente puede identificar familias de productos y proporcionar información relevante sobre ellas.",
    instruction=AGENT_INSTRUCTION,
    generate_content_config=GenerateContentConfig(
        temperature=0.3,
        max_output_tokens=2500
    ),    
    tools=[
        *AGENT_TOOLS,
    ]
)

