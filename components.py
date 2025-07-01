# EN: shared_components.py (o donde definas tus herramientas)
# VERSIÓN CORREGIDA PARA ADK v1.3.0

import logging
from enum import Enum
from google.adk.tools import FunctionTool
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

# 1. ESTADO GLOBAL (SIN CAMBIOS)
class GlobalWorkflowStatus(Enum):
    CONTINUE = "CONTINUE"
    EXIT_ALL_LOOPS = "EXIT_ALL_LOOPS"

# 2. NUEVA HERRAMIENTA DE "SEÑALIZACIÓN" (NO RECIBE CONTEXTO)
def signal_exit_loop(reason: str) -> dict:
    """
    Genera una señal para salir del bucle con una razón específica.
    Esta herramienta NO modifica el estado, solo devuelve una estructura de datos.

    Args:
        reason: La razón por la que se debe salir del bucle (proporcionada por el LLM).
    
    Returns:
        Un diccionario indicando la intención de salir y el motivo.
    """
    logger.info(f"Herramienta 'signal_exit_loop' llamada con razón: {reason}")
    # Esta es la señal que el callback buscará.
    return {
        "action": "EXIT_ALL_LOOPS",
        "reason": reason
    }

# Envolvemos la función de señalización en un FunctionTool.
# Como no tiene 'ctx', no hay problemas de parseo.
ExitLoopSignalTool = FunctionTool(func=signal_exit_loop)


# 3. VERIFICADOR DE SALIDA (SIN CAMBIOS)
class ExitConditionChecker(BaseAgent):
    """
    Agente que comprueba el estado global y escala si se debe salir.
    """
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        status = ctx.session.state.get('workflow_status', GlobalWorkflowStatus.CONTINUE)
        should_exit = (status == GlobalWorkflowStatus.EXIT_ALL_LOOPS)
        
        # Este evento detendrá el LoopAgent padre si should_exit es True.
        yield Event(
            author=self.name,
            actions=EventActions(escalate=should_exit)
        )