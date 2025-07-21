from contabilidad.prompt import IMPUESTOS_AGENT_INSTRUCTION
from contabilidad.impuestos_tools import IMPUESTOS_TOOLS
from google.adk.agents import LlmAgent
import general

ImpuestosAgent = LlmAgent(
    name="ImpuestosAgent",
    model=general.MODEL_GEMINI_2_5_FLASH,
    description="Agente especializado en gestión de impuestos",
    instruction=IMPUESTOS_AGENT_INSTRUCTION,
    generate_content_config=general.GenerateContentConfig(
        temperature=0.1,
        max_output_tokens=2000
    ),
    tools=IMPUESTOS_TOOLS,
    output_key="impuestos_output"
)