# EN: el archivo que define LoopGeneral
import logging
from google.adk.agents import LoopAgent
from dispatcher.agent import DispatcherAgent

# --- Importa el componente compartido CORRECTO ---
from components import ExitConditionChecker

logger = logging.getLogger(__name__)

# --- Configuración del Bucle General ---
LoopGeneral = LoopAgent(
    name="LoopGeneral",
    description="Bucle interno que procesa tareas.",
    sub_agents=[
        DispatcherAgent,  # Agente de trabajo principal de este bucle
        ExitConditionChecker(name="GeneralExitChecker")  # Verificador para propagar la salida
    ],
    max_iterations=3
)

root_agent = LoopGeneral  # Define el agente raíz como el bucle general