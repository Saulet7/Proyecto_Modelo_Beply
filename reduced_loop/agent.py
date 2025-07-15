# EN: el archivo que define LoopGeneral
import logging
from google.adk.agents import LoopAgent
from dispatcher.agent import DispatcherAgent, LlmAgent
from data import MODEL_GEMINI_2_0_FLASH
from google.genai.types import GenerateContentConfig
from reduced_loop.prompt import EXIT_AGENT_INSTRUCTION
from components import GlobalWorkflowStatus
from components import ExitLoopSignalTool, ExitConditionChecker

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