from google.adk.agents import LlmAgent, LoopAgent
from google.genai.types import GenerateContentConfig
from almacen_subagentes.prompt import DISPATCHER_INSTRUCTION
from data import MODEL_GEMINI_2_5_PRO
from components import ExitLoopSignalTool, ExitConditionChecker
from components import ExitLoopSignalTool

from .subagentes.almacenes_agent.agent import AlmacenesAgent
from .subagentes.atributos_agent.agent import AtributosAgent
from .subagentes.fabricantes_agent.agent import FabricantesAgent
from .subagentes.familias_agent.agent import FamiliasAgent
from .subagentes.productos_agent.agent import ProductosAgent
from .subagentes.transportista_agent.agent import TransportistasAgent
from .subagentes.srock_agent.agent import StockAgent

AlmacenesAgentCore = LlmAgent(
    name="AlmacenesAgentCore",
    model=MODEL_GEMINI_2_5_PRO,  # Usamos un modelo más potente para el dispatcher
    description="Agente coordinador que analiza consultas y las deriva al agente especializado adecuado",
    instruction=DISPATCHER_INSTRUCTION,
    generate_content_config=GenerateContentConfig(
        temperature=0.2,
        max_output_tokens=1000
    ),

    tools=[ExitLoopSignalTool],  # Herramienta para señalizar salida de bucles

    sub_agents=[
        AlmacenesAgent,
        AtributosAgent,
        FabricantesAgent,
        FamiliasAgent,
        ProductosAgent,
        StockAgent,
        TransportistasAgent
    ]
)

AlmacenesAgentLoop = LoopAgent(
    name="LoopGeneral",
    description="Bucle interno que procesa tareas.",
    sub_agents=[
        AlmacenesAgentCore,
        ExitConditionChecker(name="LoopExitChecker"),
    ],
    max_iterations=3,
)

root_agent = AlmacenesAgentCore