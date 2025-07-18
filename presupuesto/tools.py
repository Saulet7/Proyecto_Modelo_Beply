import logging
import json
from typing import Any
from utils import make_fs_request

logger = logging.getLogger(__name__)

def list_presupuestos(tool_context) -> dict:
    logger.info("TOOL EXECUTED: list_presupuestos()")
    try:
        api_result = make_fs_request("GET", "/presupuestoclientes")
        if api_result.get("status") == "success":
            data = api_result.get("data", [])
            api_result.setdefault("message_for_user", f"Encontrados {len(data)} presupuestos en el sistema.")
        else:
            api_result.setdefault("message_for_user", f"No pude obtener la lista de presupuestos. Error: {api_result.get('message', 'desconocido')}.")
        return api_result
    except Exception as e:
        logger.exception("Error al listar presupuestos")
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al obtener la lista de presupuestos: {str(e)}"
        }

def get_presupuesto(tool_context, presupuesto_id: str) -> dict:
    logger.info(f"TOOL EXECUTED: get_presupuesto(presupuesto_id='{presupuesto_id}')")
    try:
        api_result = make_fs_request("GET", f"/presupuestoclientes/{presupuesto_id}")
        if api_result.get("status") == "success":
            numero = api_result.get("data", {}).get("numero", "Sin número")
            api_result.setdefault("message_for_user", f"Presupuesto '{numero}' (ID: {presupuesto_id}) obtenido correctamente.")
        else:
            api_result.setdefault("message_for_user", f"No pude encontrar el presupuesto con ID {presupuesto_id}. Error: {api_result.get('message', 'desconocido')}.")
        return api_result
    except Exception as e:
        logger.exception(f"Error al obtener presupuesto {presupuesto_id}")
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al obtener información del presupuesto {presupuesto_id}: {str(e)}"
        }

def create_presupuesto(tool_context, cliente: str, **kwargs: Any) -> dict:
    logger.info(f"TOOL EXECUTED: create_presupuesto(cliente='{cliente}', kwargs={kwargs})")

    required_fields = {
        "cliente": cliente,
        "serie": kwargs.get("serie"),
        "fecha": kwargs.get("fecha"),
        "importe": kwargs.get("importe"),
        "forma_pago": kwargs.get("forma_pago"),
    }

    missing_fields = [key for key, value in required_fields.items() if not value]
    if missing_fields:
        return {
            "status": "error",
            "message": f"Faltan los siguientes campos obligatorios: {', '.join(missing_fields)}",
            "message_for_user": f"Faltan campos obligatorios para crear el presupuesto: {', '.join(missing_fields)}"
        }

    form_data = {**required_fields, **kwargs}

    json_data = json.dumps(form_data, indent=2, ensure_ascii=False)
    logger.info(f"Datos que se enviarán a la API: {json_data}")

    try:
        api_result = make_fs_request("POST", "/presupuestoclientes", data=form_data)
        if api_result.get("status") == "success":
            numero = api_result.get("data", {}).get("numero", "Sin número")
            api_result.setdefault("message_for_user", f"Presupuesto creado con éxito para el cliente '{cliente}'. Número: {numero}.\n\nDatos enviados:\n{json_data}")
        else:
            api_result.setdefault("message_for_user", f"No pude crear el presupuesto para el cliente '{cliente}'. Error: {api_result.get('message', 'desconocido')}.\n\nDatos enviados:\n{json_data}")
        return api_result
    except Exception as e:
        logger.exception("Error al crear presupuesto")
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al crear presupuesto: {str(e)}"
        }

def update_presupuesto(tool_context, presupuesto_id: str, **kwargs: Any) -> dict:
    logger.info(f"TOOL EXECUTED: update_presupuesto(presupuesto_id='{presupuesto_id}', kwargs={kwargs})")

    if not presupuesto_id:
        return {
            "status": "error",
            "message": "ID del presupuesto es obligatorio.",
            "message_for_user": "Necesito el ID del presupuesto para actualizarlo."
        }

    if not kwargs:
        return {
            "status": "error",
            "message": "No hay datos para actualizar.",
            "message_for_user": "No has proporcionado ningún dato para actualizar el presupuesto."
        }

    try:
        api_result = make_fs_request("PUT", f"/presupuestoclientes/{presupuesto_id}", data=kwargs)
        if api_result.get("status") == "success":
            api_result.setdefault("message_for_user", f"Presupuesto con ID {presupuesto_id} actualizado exitosamente.")
        else:
            api_result.setdefault("message_for_user", f"No pude actualizar el presupuesto con ID {presupuesto_id}. Error: {api_result.get('message', 'desconocido')}.")
        return api_result
    except Exception as e:
        logger.exception(f"Error al actualizar presupuesto {presupuesto_id}")
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al actualizar presupuesto {presupuesto_id}: {str(e)}"
        }

def delete_presupuesto(tool_context, presupuesto_id: str) -> dict:
    logger.info(f"TOOL EXECUTED: delete_presupuesto(presupuesto_id='{presupuesto_id}')")

    if not presupuesto_id:
        return {
            "status": "error",
            "message": "ID del presupuesto es obligatorio.",
            "message_for_user": "Necesito el ID del presupuesto para poder eliminarlo."
        }

    try:
        api_result = make_fs_request("DELETE", f"/presupuestoclientes/{presupuesto_id}")
        if api_result.get("status") == "success":
            api_result.setdefault("message_for_user", f"Presupuesto con ID {presupuesto_id} eliminado exitosamente.")
        else:
            api_result.setdefault("message_for_user", f"No pude eliminar el presupuesto con ID {presupuesto_id}. Error: {api_result.get('message', 'desconocido')}.")
        return api_result
    except Exception as e:
        logger.exception(f"Error al eliminar presupuesto {presupuesto_id}")
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al eliminar presupuesto {presupuesto_id}: {str(e)}"
        }

# ✅ Lista final de herramientas del agente
PRESUPUESTO_AGENT_TOOLS = [
    list_presupuestos,
    get_presupuesto,
    create_presupuesto,
    update_presupuesto,
    delete_presupuesto
]
