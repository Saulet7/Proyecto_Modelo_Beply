# EN: el archivo que define LoopGeneral
import logging
from google.adk.agents import LoopAgent
from dispatcher.agent import DispatcherAgent

from components import ExitConditionChecker

logger = logging.getLogger(__name__)

ReducedLoop = LoopAgent(
    name="LoopGeneral",
    description="Bucle interno que procesa tareas.",
    sub_agents=[
        DispatcherAgent,
        ExitConditionChecker(name="LoopExitChecker"),
    ],
    max_iterations=3,
)


root_agent = ReducedLoop