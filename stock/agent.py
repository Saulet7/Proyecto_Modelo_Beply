import logging
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from stock.prompt import STOCK_AGENT_INSTRUCTION
from stock.tools import STOCK_AGENT_TOOLS
from components import ExitConditionChecker, ExitLoopSignalTool

logger = logging.getLogger(__name__)

StockAgent = LlmAgent(
    name="StockAgent",
    model="gemini-2.0-flash",
    description="Agente especializado en gestión y análisis de inventario y stock",
    instruction=STOCK_AGENT_INSTRUCTION,
    generate_content_config=GenerateContentConfig(
        temperature=0.2,
        max_output_tokens=2500
    ),
    tools=[
        *STOCK_AGENT_TOOLS,
        ExitLoopSignalTool
    ]
)