from google.adk.tools import ToolContext
import logging
from datetime import datetime
from utils import make_fs_request

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

def send_email_to_cliente(tool_context: ToolContext, correo: str, asunto: str, cuerpo: str, nombre: str) -> dict:
    """
    Envía un correo electrónico al cliente, con estructura JSON completa.
    """
    logger.info(f"TOOL EXECUTED: send_email_to_cliente(correo='{correo}', asunto='{asunto}', nombre='{nombre}')")

    if not correo or not asunto or not cuerpo or not nombre:
        return {
            "status": "error",
            "message": "Faltan campos obligatorios (correo, asunto, cuerpo, nombre)",
            "message_for_user": "Faltan datos para enviar el correo: asegúrate de incluir destinatario, asunto, mensaje y nombre del envío."
        }

    from datetime import date
    creation_date = date.today().isoformat()

    email_payload = {
        "to": correo,  # destinatario principal
        "subject": asunto,
        "body": cuerpo,
        "name": nombre,
        "creationdate": creation_date,
        "enabled": True
    }

    try:
        # ⚠️ Ajusta este endpoint si es diferente
        api_result = make_fs_request("POST", "/emailnotifications", data=email_payload)

        if api_result.get("status") == "success":
            api_result.setdefault("message_for_user", f"Correo enviado correctamente a {correo}.")
        else:
            api_result.setdefault("message_for_user", f"No se pudo enviar el correo a {correo}. Error: {api_result.get('message', 'desconocido')}.")

        return api_result

    except Exception as e:
        logger.exception("Error al enviar correo")
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al enviar el correo a {correo}: {str(e)}"
        }
