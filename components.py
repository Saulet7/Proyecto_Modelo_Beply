# EN: shared_components.py (o donde definas tus herramientas)
# VERSIÓN CORREGIDA PARA ADK v1.3.0

import logging
from enum import Enum
from google.adk.tools import FunctionTool
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from typing import AsyncGenerator
from google.adk.tools.tool_context import ToolContext


logger = logging.getLogger(__name__)

# 1. ESTADO GLOBAL
class GlobalWorkflowStatus(Enum):
    CONTINUE = "CONTINUE"
    EXIT_ALL_LOOPS = "EXIT_ALL_LOOPS"

# 2. HERRAMIENTA DE "SEÑALIZACIÓN" PARA SALIR DE TODOS LOS BUCLES
def signal_exit_loop(tool_context: ToolContext, reason: str = "No reason provided.") -> dict:
    """
    Herramienta para salir de TODOS los bucles con una razón específica.

    Esta función no modifica el estado directamente, solo eleva la acción y devuelve una señal.

    Args:
        tool_context: Contexto de ejecución proporcionado por ADK.
        reason: La razón por la que se debe salir del bucle.

    Returns:
        Un diccionario estructurado indicando la intención de salida y el motivo.
    """
    logger.info(f"[Tool] signal_exit_loop llamada por '{tool_context.agent_name}' con razón: {reason}")

    tool_context.actions.escalate = True

    return {
        "action": "EXIT_ALL_LOOPS",
        "reason": reason
    }


# Envolvemos las funciones de señalización en FunctionTool.
# Como no tienen 'ctx', no hay problemas de parseo.
ExitLoopSignalTool = FunctionTool(func=signal_exit_loop)

class ExitConditionChecker(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        status = ctx.session.state.get('workflow_status', GlobalWorkflowStatus.CONTINUE)
        exit_reason = ctx.session.state.get('exit_reason', 'Razón no especificada.')
        
        # Add logic here for ExitAgent to also identify "missing specific data"
        # For example, if it receives an empty input or recognizes a pattern
        # This would require it to be an LlmAgent that can process user input / previous agent output

        if status == GlobalWorkflowStatus.EXIT_ALL_LOOPS:
            yield Event(
                author=self.name,
                actions=EventActions(
                    escalate=True,
                    stateDelta={'exit_event_details': {'exit_type': 'all_loops', 'reason': exit_reason}}
                )
            )
        # ELSE: If ExitAgent's role is also to determine missing data for *continuation*,
        # it would need to set specific flags in session.state for the Dispatcher to read.
        # This makes ExitAgent very complex; often, missing data is handled by the
        # LlmAgent attempting the task.
        else:
            logger.debug("ExitConditionChecker: No hay señal de salida total, el bucle continúa.")