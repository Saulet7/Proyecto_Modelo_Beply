# EN: el archivo que define ValidationLoopAgent
import logging
from google.adk.agents import LlmAgent, LoopAgent
from google.genai.types import GenerateContentConfig
from data import MODEL_GEMINI_2_0_FLASH
from loop_validacion.prompt import VALIDATION_AGENT_INSTRUCTION
from emergency_loop.agent import EmergencyLoopAgent

# --- Importa los componentes compartidos CORRECTOS ---
from components import (
    ExitConditionChecker,
    ExitLoopSignalTool,  # <-- La nueva herramienta de señalización
    GlobalWorkflowStatus,
    ExitCurrentLoopSignalTool
)
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import BaseTool
from typing import Dict, Any

logger = logging.getLogger(__name__)

# --- Callback para procesar la señal de salida ---
# (Este callback puede vivir aquí o en un archivo de componentes compartidos)
def process_exit_signal_callback(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: CallbackContext,
    tool_response: Dict
) -> None:
    """
    Revisa la respuesta de una herramienta y actualiza el estado si es una señal de salida.
    """
    if tool.name == "signal_exit_loop" and isinstance(tool_response, dict):
        if tool_response.get("action") == "EXIT_ALL_LOOPS":
            tool_context.state['workflow_status'] = GlobalWorkflowStatus.EXIT_ALL_LOOPS
            tool_context.state['exit_reason'] = tool_response.get("reason", "Sin razón específica")
            logger.warning(f"CALLBACK: Señal de salida detectada en ValidationAgent.")

    elif tool.name == "signal_exit_current_loop" and isinstance(tool_response, dict):
        if tool_response.get("action") == "EXIT_CURRENT_LOOP":
            tool_context.state['workflow_status'] = GlobalWorkflowStatus.EXIT_CURRENT_LOOP
            tool_context.state['exit_reason'] = tool_response.get("reason", "Sin razón específica")
            logger.info(f"CALLBACK: Señal de salida del bucle actual detectada en ValidationAgent.")

# --- Configuración del Agente de Validación ---
ValidationAgent = LlmAgent(
    name="ValidationAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Agente validador final que también puede activar la salida.",
    instruction=VALIDATION_AGENT_INSTRUCTION,
    
    # 1. Usa la herramienta de SEÑALIZACIÓN
    tools=[ExitLoopSignalTool, ExitCurrentLoopSignalTool],
    
    # 2. Usa el CALLBACK para procesar la señal
    after_tool_callback=process_exit_signal_callback,
    
    generate_content_config=GenerateContentConfig(
        temperature=0.0,
        max_output_tokens=2000
    )
)

# --- Configuración del Bucle de Validación (Agente de más alto nivel) ---
ValidationLoopAgent = LoopAgent(
    name="ValidationLoopAgent",
    description="Agente de validación de más alto nivel",
    sub_agents=[
        EmergencyLoopAgent,  # Contiene a LoopGeneral dentro
        ValidationAgent,
        ExitConditionChecker(name="PreValidationExitChecker"),  # Primero verifica condiciones
    ],
    max_iterations=3
)