import logging
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from data import MODEL_GEMINI_2_5_FLASH
from presupuesto.prompt import PRESUPUESTO_AGENT_INSTRUCTION
from presupuesto.tools import PRESUPUESTO_AGENT_TOOLS
from components import ExitLoopSignalTool

logger = logging.getLogger(__name__)

PresupuestoAgent = LlmAgent(
    name="PresupuestoAgent",
    model=MODEL_GEMINI_2_5_FLASH,
    description="Agente especializado en gestión, análisis y procesamiento de presupuestos.",
    instruction=PRESUPUESTO_AGENT_INSTRUCTION,
    generate_content_config=GenerateContentConfig(
        temperature=0.2,
        max_output_tokens=2500
    ),
    tools=[
        *PRESUPUESTO_AGENT_TOOLS
    ]
)
