import logging
from google.adk.agents import LlmAgent, LoopAgent
from google.genai.types import GenerateContentConfig
from components import ExitLoopSignalTool, ExitConditionChecker
from data import MODEL_GEMINI_2_5_PRO
from almacen_simple.prompt import ALMACEN_AGENT_INSTRUCTION
from almacen_simple.tools import ALMACEN_AGENT_TOOLS

logger = logging.getLogger(__name__)

AlmacenAgent = LlmAgent(
    name="AlmacenAgent",
    model=MODEL_GEMINI_2_5_PRO,
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

AlmacenLoop = LoopAgent(
    name="LoopGeneral",
    description="Bucle interno que procesa tareas.",
    sub_agents=[
        AlmacenAgent,
        ExitConditionChecker(name="LoopExitChecker"),
    ],
    max_iterations=3,
)

root_agent = AlmacenLoop