import os
import logging
import json
from dotenv import load_dotenv
from google.adk.run import run_agent

# Make sure these imports are correct based on your project structure
# For example, if contabilidad/agent.py defines ContabilidadAgent and root_agent
from contabilidad.agent import ContabilidadAgent, root_agent 

# --- Configuration ---
# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ContabilidadAgentTest")

# --- Test Program ---
def test_contabilidad_agent_flow():
    """
    Tests the basic conversational flow of the ContabilidadAgent using
    google.adk.run.
    """
    logger.info("🧪 Iniciando test conversacional con ContabilidadAgent...\n")

    # Define the conversational messages for the test flow
    test_messages = [
        "Listame todos los asientos contables",
        "Crea un asiento con canal 1, ejercicio 2024, concepto 'Compra de material', documento FAC-001, editable, fecha 2025-07-21, diario 1, empresa 1, numero AS-TEST-001, operación Compra",
        "Ahora muestra ese asiento recién creado",
        "Actualiza el concepto a 'Compra de material actualizada' para el asiento que acabamos de crear", # More specific prompt
        "Listame las cuentas disponibles"
    ]

    # Context to maintain conversation state across turns
    # ADK's run_agent manages this state internally, but you can
    # initialize it here if you need to pass specific starting parameters.
    state = {
        "app_name": "test_contabilidad",
        "user_id": "test_user_123",
        # You might store specific IDs here if your agent needs them for follow-up actions,
        # but ideally, the agent's internal state or tool outputs manage this.
    }
    
    # Store all responses for later analysis
    all_responses = []

    for i, message in enumerate(test_messages):
        logger.info(f"\n--- Turno {i+1} ---")
        logger.info(f"👤 Usuario: {message}")

        try:
            # The recommended way to interact with an ADK agent
            # The 'state' will be updated by the agent and persisted across calls
            response = run_agent(
                agent=ContabilidadAgent,  # Pass your agent class/instance
                query=message,
                state=state,              # Pass the state dictionary
                stream=False              # For tests, usually prefer non-streaming
            )
            
            # ADK's run_agent typically returns a dictionary or object
            # You'll need to know the structure of your agent's output.
            # Assuming it returns a dictionary with a 'text' or 'output' key
            agent_output = response.get("text", str(response)) 
            
            logger.info(f"🤖 Agente: {agent_output}")
            
            # Capture the full response object and the state after the turn
            all_responses.append({
                "turn": i + 1,
                "query": message,
                "agent_response": response,
                "current_state_after_turn": state.copy() # Store a copy of the state
            })

        except Exception as e:
            logger.error(f"❌ Error en el turno {i+1} para el mensaje '{message}': {e}", exc_info=True)
            all_responses.append({
                "turn": i + 1,
                "query": message,
                "error": str(e),
                "current_state_after_turn": state.copy()
            })
            # Optionally break if an error is critical, or continue to see subsequent failures
            # break 

    # Save detailed results to a JSON file
    output_filename = "contabilidad_test_results.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(all_responses, f, indent=2, ensure_ascii=False)

    logger.info(f"\n✅ Test completado. Resultados detallados guardados en {output_filename}")
    logger.info("ℹ️ Revisa el archivo JSON para el análisis completo de las respuestas y estados.")

# --- Main Execution ---
if __name__ == "__main__":
    # Before running:
    # 1. Ensure your 'contabilidad' package (specifically contabilidad/agent.py) is accessible.
    # 2. Verify that ContabilidadAgent and root_agent are correctly defined within it.
    # 3. Check your .env file for any necessary environment variables.
    
    test_contabilidad_agent_flow()