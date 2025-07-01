import logging
from google.adk.agents import SequentialAgent, LlmAgent
from google.genai.types import GenerateContentConfig
from data import MODEL_GEMINI_2_0_FLASH
from loop_validacion.agent import ValidationLoopAgent


logger = logging.getLogger(__name__)

FormatAgent = LlmAgent(
    name="FormatAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Agente encargado de formatear y estructurar la información antes de su entrega final.",
    global_instruction="Asegúrate de que la información está bien estructurada y lista para ser validada.",
    
    generate_content_config=GenerateContentConfig(
        temperature=0.0,
        max_output_tokens=2000
    )
)


GeneralFluxAgent = SequentialAgent(
    name="GeneralFluxAgent",
    description="Agente orquestador para gestionar el flujo de conversación en el sistema integración financiero en empresas.",
    sub_agents=[
        ValidationLoopAgent,   # Agente especializado en errores
        FormatAgent,
    ]
)

root_agent = GeneralFluxAgent