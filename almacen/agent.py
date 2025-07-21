import logging
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from data import MODEL_GEMINI_2_5_FLASH
from almacen.prompt import ALMACEN_AGENT_INSTRUCTION
from almacen.tools import ALMACEN_AGENT_TOOLS

logger = logging.getLogger(__name__)

AlmacenAgent = LlmAgent(
    name="AlmacenAgent",
    model=MODEL_GEMINI_2_5_FLASH,
    description="Agente especializado en la gestión de almacenes, con capacidades para identificar, analizar y documentar supuestos relacionados con procesos logísticos, inventarios y operaciones empresariales. ",
    instruction=ALMACEN_AGENT_INSTRUCTION,
    generate_content_config=GenerateContentConfig(
        temperature=0.3,
        max_output_tokens=2500
    ),    
    tools=[
        *ALMACEN_AGENT_TOOLS
    ]
)

root_agent = AlmacenAgent