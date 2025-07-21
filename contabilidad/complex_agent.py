from sub_agentes.asientos_agent import AsientosAgent
from sub_agentes.cuentas_agent import CuentasAgent
from sub_agentes.ejercicios_agent import EjerciciosAgent
from sub_agentes.formaspago_agent import FormasPagoAgent
from sub_agentes.impuestos_agent import ImpuestosAgent
from google.adk.agents import LlmAgent, AgentNetwork, DispatchAgent
from google.genai.types import GenerateContentConfig
from contabilidad.prompt import DISPATCHER_INSTRUCTION
from data import MODEL_GEMINI_2_5_PRO

DispatcherAgent = LlmAgent(
    name="DispatcherAgent",
    model=MODEL_GEMINI_2_5_PRO,  # Usamos un modelo más potente para el dispatcher
    description="Agente coordinador que analiza consultas y las deriva al agente especializado adecuado",
    instruction=DISPATCHER_INSTRUCTION,
    generate_content_config=GenerateContentConfig(
        temperature=0.2,
        max_output_tokens=1000
    ),
    agents={
        "AsientosAgent": AsientosAgent,
        "CuentasAgent": CuentasAgent,
        "EjerciciosAgent": EjerciciosAgent,
        "FormasPagoAgent": FormasPagoAgent,
        "ImpuestosAgent": ImpuestosAgent
    }
)

root_agent = DispatcherAgent