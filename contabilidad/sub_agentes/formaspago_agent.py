from contabilidad.prompt import FORMASPAGO_AGENT_INSTRUCTION
from formaspago_tools import FORMASPAGO_TOOLS
from google.adk.agents import LlmAgent
import general


FormasPagoAgent = LlmAgent(
    name="FormasPagoAgent",
    model=general.MODEL_GEMINI_2_5_FLASH,
    description="Agente especializado en gestión de formas de pago",
    instruction=FORMASPAGO_AGENT_INSTRUCTION,
    generate_content_config=general.GenerateContentConfig(
        temperature=0.1,
        max_output_tokens=2000
    ),
    tools=FORMASPAGO_TOOLS,
    output_key="formaspago_output"
)