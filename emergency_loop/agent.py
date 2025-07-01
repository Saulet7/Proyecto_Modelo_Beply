import logging
from dispatcher.agent import DispatcherAgent
from google.adk.agents import LlmAgent, LoopAgent, BaseAgent
from google.genai.types import GenerateContentConfig
from data import MODEL_GEMINI_2_0_FLASH
from emergency_loop.prompt import EMERGENCY_AGENT_INSTRUCTION
from loop_general.agent import LoopGeneral
from google.adk.agents.invocation_context import InvocationContext
from components import ExitConditionChecker, GlobalWorkflowStatus, ExitLoopSignalTool  # Importa el verificador de condición de salida
# EN: El archivo donde defines tu EmergencyAgent (por ejemplo)
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import BaseTool
from typing import Dict, Any

# 2. Función exit_loop modificada para usar session.state
# 1. DEFINE EL CALLBACK
def process_exit_signal_callback(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: CallbackContext,
    tool_response: Dict
) -> None:
    """
    Callback que se ejecuta DESPUÉS de una llamada a herramienta.
    Revisa si la respuesta de la herramienta es una señal de salida y actualiza el estado.
    """
    if tool.name == "signal_exit_loop" and isinstance(tool_response, dict):
        if tool_response.get("action") == "EXIT_ALL_LOOPS":
            # Si se detecta la señal, se modifica el estado global.
            tool_context.state['workflow_status'] = GlobalWorkflowStatus.EXIT_ALL_LOOPS
            tool_context.state['exit_reason'] = tool_response.get("reason", "Sin razón específica")
            print(f"CALLBACK: Señal de salida detectada. Estado actualizado.")

# 2. CONFIGURA TU AGENTE PARA USAR LA HERRAMIENTA Y EL CALLBACK
EmergencyAgent = LlmAgent(
    name="EmergencyAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Agente que detecta errores y puede activar la salida global.",
    instruction="""Si detectas una condición de error irreversible o una solicitud explícita de salida, 
                 DEBES llamar a la herramienta 'signal_exit_loop' con una descripción clara de la razón.""",
    
    tools=[
        ExitLoopSignalTool  # <-- Usa la nueva herramienta de señalización.
    ],
    
    # LA CLAVE ESTÁ AQUÍ:
    after_tool_callback=process_exit_signal_callback
)

# 5. EmergencyLoopAgent configurado para manejar eventos de salida
EmergencyLoopAgent = LoopAgent(
    name="EmergencyLoopAgent",
    description="Bucle que gestiona emergencias y contiene el bucle general.",
    sub_agents=[
        LoopGeneral,        # 1. Ejecuta el bucle interno
        EmergencyAgent,     # 2. Después, ejecuta el agente de emergencia
        ExitConditionChecker(name="EmergencyExitChecker") # 3. Verifica si debe salir de ESTE bucle
    ],
    max_iterations=3
)