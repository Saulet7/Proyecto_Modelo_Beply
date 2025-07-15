# EN: dispatcher/agent.py
import logging
from google.adk.agents import LlmAgent
from google.adk.tools import BaseTool
from google.adk.agents.callback_context import CallbackContext
from typing import Dict, Any

# Importa los agentes "hijos"
from factura.agent import FacturaAgent
from cliente.agent import ClienteAgent
from stock.agent import StockAgent
from producto.agent import ProductoAgent  
from proveedor.agent import ProveedorAgent  # Nuevo agente de Producto
# Importa el prompt y las herramientas/componentes compartidos
from dispatcher.prompt import GENERAL_AGENT_PROMPT, AGENT_PROMPT
from components import ExitLoopSignalTool, ExitCurrentLoopSignalTool, GlobalWorkflowStatus
from data import MODEL_GEMINI_2_0_FLASH

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


# Definición del DispatcherAgent como Orquestador Interno
DispatcherAgent = LlmAgent(
    name="DispatcherAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Agente orquestador que gestiona el flujo de conversación y llama a sub-agentes especializados.",
    instruction=GENERAL_AGENT_PROMPT,
    
    # Herramientas: Ambas señales de salida
    # La herramienta 'transfer_to_agent' se usa para llamar a los sub-agentes listados abajo.
    tools=[
        ExitLoopSignalTool,          # Salir de todos los bucles
    ],
    
    # ¡CRÍTICO! Aquí es donde defines que FacturaAgent y ClienteAgent son "hijos"
    # que este agente puede invocar.
    sub_agents=[
        FacturaAgent,
        ClienteAgent,
        StockAgent,
        ProductoAgent,  # Nuevo agente añadido
        ProveedorAgent,  # Agente de Proveedor
    ],

    after_tool_callback=process_exit_signal_callback,  # Callback para procesar señales de salida

    output_key="dispatcher_output"
)