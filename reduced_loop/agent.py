# EN: el archivo que define LoopGeneral
import logging
from google.adk.agents import LoopAgent
from dispatcher.agent import DispatcherAgent, LlmAgent
from data import MODEL_GEMINI_2_0_FLASH
from google.genai.types import GenerateContentConfig
from reduced_loop.prompt import EXIT_AGENT_INSTRUCTION

from components import ExitLoopSignalTool, ExitConditionChecker

logger = logging.getLogger(__name__)


ExitAgent = LlmAgent(
    name="ExitAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Agente encargado de verificar condiciones de salida del bucle general.",
    instruction=EXIT_AGENT_INSTRUCTION,
    tools=[ExitLoopSignalTool],  # Herramienta para señalizar salida
    generate_content_config=GenerateContentConfig(
        temperature=0.0,
        max_output_tokens=2000
    )
)

# --- Configuración del Bucle General ---
ReducedLoop = LoopAgent(
    name="LoopGeneral",
    description="Bucle interno que procesa tareas.",
    sub_agents=[
        DispatcherAgent, # Agente de trabajo principal de este bucle
        ExitConditionChecker(name="LoopExitChecker"), # Le damos un nombre único
    ],
    max_iterations=10, # Sigue manteniendo un límite de iteraciones como fallback
    # Añadimos un callback para procesar los eventos de los sub-agentes
)

root_agent = ReducedLoop