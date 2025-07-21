from contabilidad.prompt import EJERCICIOS_AGENT_INSTRUCTION
from contabilidad.ejercicios_tools import EJERCICIOS_TOOLS
from google.adk.agents import LlmAgent
import general

EjerciciosAgent = LlmAgent(
    name="EjerciciosAgent",
    model=general.MODEL_GEMINI_2_5_FLASH,
    description="Agente especializado en gestión de ejercicios contables",
    instruction=EJERCICIOS_AGENT_INSTRUCTION,
    generate_content_config=general.GenerateContentConfig(
        temperature=0.1,
        max_output_tokens=2000
    ),
    tools=EJERCICIOS_TOOLS,
    output_key="ejercicios_output"
)