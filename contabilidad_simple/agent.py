import logging
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from data import MODEL_GEMINI_2_5_FLASH
from contabilidad_simple.prompt import CONTABILIDAD_AGENT_INSTRUCTION

# Importar todas las herramientas de contabilidad
from contabilidad_simple.asientos_tools import ASIENTOS_TOOLS
from contabilidad_simple.cuentas_tools import CUENTAS_TOOLS
from contabilidad_simple.ejercicios_tools import EJERCICIOS_TOOLS
from contabilidad_simple.formaspago_tools import FORMASPAGO_TOOLS
from contabilidad_simple.impuestos_tools import IMPUESTOS_TOOLS

logger = logging.getLogger(__name__)

# Combinar todas las herramientas de contabilidad
CONTABILIDAD_TOOLS = [
    # Herramientas de asientos contables
    *ASIENTOS_TOOLS,
    
    # Herramientas de cuentas contables
    *CUENTAS_TOOLS,
    
    # Herramientas de ejercicios contables
    *EJERCICIOS_TOOLS,
    
    # Herramientas de formas de pago
    *FORMASPAGO_TOOLS,
    
    # Herramientas de impuestos
    *IMPUESTOS_TOOLS
]

ContabilidadAgent = LlmAgent(
    name="ContabilidadAgent",
    model=MODEL_GEMINI_2_5_FLASH,
    description="Agente especializado en gestión integral de contabilidad: asientos, cuentas, ejercicios, formas de pago e impuestos",
    instruction=CONTABILIDAD_AGENT_INSTRUCTION,
    generate_content_config=GenerateContentConfig(
        temperature=0.2,
        max_output_tokens=3000
    ),
    tools=CONTABILIDAD_TOOLS,
    output_key="contabilidad_output"
)

logger.info(f"ContabilidadAgent creado exitosamente con {len(CONTABILIDAD_TOOLS)} herramientas disponibles")

# Log de herramientas disponibles para debug
tool_names = [tool.__name__ for tool in CONTABILIDAD_TOOLS]
logger.info(f"Herramientas disponibles: {', '.join(tool_names)}")

root_agent = ContabilidadAgent  # ¡Esto es lo crucial!