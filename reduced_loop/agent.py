# EN: el archivo que define LoopGeneral
import logging
from google.adk.agents import LoopAgent
from dispatcher.agent import DispatcherAgent, LlmAgent
from data import MODEL_GEMINI_2_0_FLASH
from google.genai.types import GenerateContentConfig
from reduced_loop.prompt import EXIT_AGENT_INSTRUCTION

from components import ExitLoopSignalTool, ExitConditionChecker

logger = logging.getLogger(__name__)

# --- Configuración del Bucle General ---
ReducedLoop = LoopAgent(
    name="LoopGeneral",
    description="Bucle interno que procesa tareas.",
    sub_agents=[
        DispatcherAgent, # Agente de trabajo principal de este bucle
        ExitConditionChecker(name="LoopExitChecker"), # Le damos un nombre único
    ],
    max_iterations=3, # Sigue manteniendo un límite de iteraciones como fallback
    # Añadimos un callback para procesar los eventos de los sub-agentes
)

root_agent = ReducedLoop