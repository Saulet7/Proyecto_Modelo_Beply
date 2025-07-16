import logging
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from data import MODEL_GEMINI_2_5_FLASH
from cliente.prompt import CLIENTE_AGENT_INSTRUCTION
from cliente.tools import CLIENTE_AGENT_TOOLS

logger = logging.getLogger(__name__)

ClienteAgent = LlmAgent(
    name="ClienteAgent",
    model=MODEL_GEMINI_2_5_FLASH,
    description="Agente especializado en identificación, análisis y documentación de supuestos en procesos empresariales",
    instruction=CLIENTE_AGENT_INSTRUCTION,
    generate_content_config=GenerateContentConfig(
        temperature=0.3,
        max_output_tokens=2500
    ),    
    tools=[
        *CLIENTE_AGENT_TOOLS
    ]
)

