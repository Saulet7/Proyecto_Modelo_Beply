import logging
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from data import MODEL_GEMINI_2_5_FLASH
from almacenes_agent.prompt import AGENT_INSTRUCTION
from almacenes_agent.tools import AGENT_TOOLS
from components import ExitLoopSignalTool

logger = logging.getLogger(__name__)

AlmacenesAgent = LlmAgent(
    name="AlmacenesAgent",
    model=MODEL_GEMINI_2_5_FLASH,
    description="Agente especializado en gestión de almacenes",
    instruction=AGENT_INSTRUCTION,
    generate_content_config=GenerateContentConfig(
        temperature=0.2,
        max_output_tokens=2500
    ),
    tools=[
        *AGENT_TOOLS
    ]
)