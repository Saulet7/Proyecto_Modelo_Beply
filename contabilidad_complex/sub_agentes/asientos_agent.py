from contabilidad_simple.prompt import ASIENTOS_AGENT_INSTRUCTION
from contabilidad_simple.asientos_tools import ASIENTOS_TOOLS
from google.adk.agents import LlmAgent
import contabilidad_complex.general as general

AsientosAgent = LlmAgent(
    name="AsientosAgent",
    model=general.MODEL_GEMINI_2_5_FLASH,
    description="Agente especializado en gestión de asientos contables",
    instruction=ASIENTOS_AGENT_INSTRUCTION,
    generate_content_config=general.GenerateContentConfig(
        temperature=0.1,
        max_output_tokens=2000
    ),
    tools=ASIENTOS_TOOLS,
    output_key="asientos_output"
)