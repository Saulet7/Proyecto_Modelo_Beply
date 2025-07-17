# EN: dispatcher/agent.py
import logging
from google.adk.agents import LlmAgent
from google.adk.tools import BaseTool
from google.adk.agents.callback_context import CallbackContext
from typing import Dict, Any

# Importa los agentes "hijos"
from creador_factura.agent import CreadorFacturaAgent
from linea_factura.agent import LineaFacturaAgent
from cliente.agent import ClienteAgent
from stock.agent import StockAgent
from producto.agent import ProductoAgent
from proveedor.agent import ProveedorAgent
from fabricante.agent import FabricanteAgent
from familia.agent import FamiliaAgent
# Importa el prompt y las herramientas/componentes compartidos
from dispatcher.prompt import GENERAL_AGENT_PROMPT, AGENT_PROMPT
from dispatcher.tools import get_current_time
from components import ExitLoopSignalTool, GlobalWorkflowStatus
from data import MODEL_GEMINI_2_5_PRO

logger = logging.getLogger(__name__)

# Callback para procesar las señales de salida (actualizado)
def process_exit_signal_callback(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: CallbackContext,
    tool_response: Dict
) -> None:
    if tool.name == "signal_exit_loop" and isinstance(tool_response, dict):
        if tool_response.get("action") == "EXIT_ALL_LOOPS":
            tool_context.state['workflow_status'] = GlobalWorkflowStatus.EXIT_ALL_LOOPS
            tool_context.state['exit_reason'] = tool_response.get("reason", "Razón no especificada por Dispatcher")
            logger.warning(f"CALLBACK: DispatcherAgent activó la señal de salida de TODOS los bucles.")

# Nuevo Callback para procesar la salida de los sub-agentes
def after_sub_agent_call_callback(
    tool: BaseTool, # En este caso, 'tool' será la herramienta 'transfer_to_agent'
    args: Dict[str, Any],
    tool_context: CallbackContext,
    tool_response: Dict # Contiene la respuesta y el estado del sub-agente
) -> None:
    """
    Callback que se ejecuta después de que el DispatcherAgent llama a un sub-agente.
    Monitorea la respuesta del sub-agente para detectar señales de salida o preguntas.
    """
    if isinstance(tool_response, dict):
        sub_agent_output = tool_response.get("response") # La respuesta textual o de herramienta del sub-agente
        sub_agent_name = tool_response.get("agent_name", "UnknownAgent")

        # Prioridad: ¿El sub-agente intentó explicitamente una salida?
        if isinstance(sub_agent_output, dict) and sub_agent_output.get("action") == "EXIT_ALL_LOOPS":
            tool_context.state['workflow_status'] = GlobalWorkflowStatus.EXIT_ALL_LOOPS
            tool_context.state['exit_reason'] = sub_agent_output.get("reason", f"Salida solicitada por {sub_agent_name}")
            logger.warning(f"CALLBACK: Sub-agente '{sub_agent_name}' activó señal de salida de TODOS los bucles.")
            return

        # Detección adicional: ¿La respuesta del sub-agente es una pregunta?
        # Asegúrate de que esta lógica sea coherente con tu prompt y CreadorFacturaAgent, etc.
        question_patterns = [
            "Necesito", "necesito", "¿Cuál", "cuál", "Por favor proporciona",
            "por favor, proporciona", "por favor envía", "Requiero",
            "dame", "dime", "indícame", "falta"
        ]
        if isinstance(sub_agent_output, str) and any(pattern in sub_agent_output for pattern in question_patterns):
            tool_context.state['workflow_status'] = GlobalWorkflowStatus.EXIT_ALL_LOOPS
            tool_context.state['exit_reason'] = f"Pregunta detectada de {sub_agent_name} - Esperando respuesta del usuario"
            logger.warning(f"CALLBACK: Forzando salida por pregunta detectada de {sub_agent_name}: '{sub_agent_output[:50]}...'")
            return


# Definición del DispatcherAgent como Orquestador Interno
DispatcherAgent = LlmAgent(
    name="DispatcherAgent",
    model=MODEL_GEMINI_2_5_PRO,
    description="Agente orquestador que gestiona el flujo de conversación y llama a sub-agentes especializados.",
    instruction=GENERAL_AGENT_PROMPT,

    tools=[
        get_current_time,  # Registrar timestamp de solicitudes
        ExitLoopSignalTool, # Salir de todos los bucles
    ],

    sub_agents=[
        CreadorFacturaAgent,
        ClienteAgent,
        StockAgent,
        ProductoAgent,
        ProveedorAgent,
        FabricanteAgent,
        FamiliaAgent,
        LineaFacturaAgent
    ],

    after_tool_callback=process_exit_signal_callback,
    output_key="dispatcher_output"
)