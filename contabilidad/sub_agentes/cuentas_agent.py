from contabilidad.prompt import CUENTAS_AGENT_INSTRUCTION
from contabilidad.cuentas_tools import CUENTAS_TOOLS
from google.adk.agents import LlmAgent
import general

CuentasAgent = LlmAgent(
    name="CuentasAgent",
    model=general.MODEL_GEMINI_2_5_FLASH,
    description="Agente especializado en gestión de cuentas contables",
    instruction=CUENTAS_AGENT_INSTRUCTION,
    generate_content_config=general.GenerateContentConfig(
        temperature=0.1,
        max_output_tokens=2000
    ),
    tools=CUENTAS_TOOLS,
    output_key="cuentas_output"
)