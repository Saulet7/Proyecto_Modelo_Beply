from google.adk.tools import ToolContext

# --- Herramienta para salir del bucle ---
def exit_processing_loop(tool_context: ToolContext):
    """Función que se llama cuando la pregunta está validada para salir del bucle"""
    print(f"[Tool Call] exit_processing_loop llamado por {tool_context.agent_name}")
    tool_context.actions.escalate = True
    return {"status": "validated"}