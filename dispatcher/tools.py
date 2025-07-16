from google.adk.tools import ToolContext
import logging
from datetime import datetime

# --- Herramienta para salir del bucle ---
def exit_processing_loop(tool_context: ToolContext):
    """Función que se llama cuando la pregunta está validada para salir del bucle"""
    print(f"[Tool Call] exit_processing_loop llamado por {tool_context.agent_name}")
    tool_context.actions.escalate = True
    return {"status": "validated"}

logger = logging.getLogger(__name__)

def get_current_time(tool_context: ToolContext):
    """
    Devuelve la hora y fecha actual en formato legible para el usuario.
    """
    now = datetime.now()
    hora_formateada = now.strftime("%H:%M:%S")
    fecha_formateada = now.strftime("%d/%m/%Y")

    return {
        "status": "success",
        "time": hora_formateada,
        "date": fecha_formateada,
        "message_for_user": f"La hora actual es {hora_formateada} del día {fecha_formateada}."
    }
