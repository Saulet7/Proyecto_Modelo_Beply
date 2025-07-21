from contabilidad.prompt import ASIENTOS_AGENT_INSTRUCTION
from contabilidad.asientos_tools import ASIENTOS_TOOLS
from google.adk.agents import LlmAgent
import general

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