import logging
from typing import Optional, Any
from utils import make_fs_request

logger = logging.getLogger(__name__)

def list_families(tool_context):
    logger.info("TOOL EXECUTED: list_families()")
    try:
        api_result = make_fs_request("GET", "/familias")
        if api_result.get("status") == "success":
            data = api_result.get("data", [])
            api_result.setdefault("message_for_user", f"Se encontraron {len(data)} familias.")
        else:
            api_result.setdefault("message_for_user", "No se pudo obtener la lista de familias.")
        return api_result
    except Exception as e:
        logger.error(f"Error en list_families: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al listar familias: {str(e)}"
        }

def create_family(tool_context, codigo: str, descripcion: str, **kwargs):
    logger.info(f"TOOL EXECUTED: create_family(codigo='{codigo}', descripcion='{descripcion}')")

    if not codigo or not descripcion:
        return {
            "status": "error",
            "message": "Código y descripción son obligatorios.",
            "message_for_user": "Debes indicar el código y la descripción de la familia."
        }

    data = {"codigo": codigo, "descripcion": descripcion}
    data.update(kwargs)

    try:
        response = make_fs_request("POST", "/familias", data=data)
        if response.get("status") == "success":
            response.setdefault("message_for_user", f"Familia '{codigo}' creada correctamente.")
        else:
            response.setdefault("message_for_user", f"No se pudo crear la familia '{codigo}'.")
        return response
    except Exception as e:
        logger.error(f"Error en create_family: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al crear la familia: {str(e)}"
        }

def update_family(tool_context, id: str, **kwargs):
    logger.info(f"TOOL EXECUTED: update_family(id='{id}')")

    if not id:
        return {
            "status": "error",
            "message": "El ID de la familia es obligatorio para actualizar.",
            "message_for_user": "Debes indicar el ID de la familia que deseas modificar."
        }

    if not kwargs:
        return {
            "status": "error",
            "message": "No se proporcionaron campos para actualizar.",
            "message_for_user": "Debes indicar al menos un campo para modificar en la familia."
        }

    try:
        response = make_fs_request("PUT", f"/familias/{id}", data=kwargs)
        if response.get("status") == "success":
            response.setdefault("message_for_user", f"Familia actualizada correctamente.")
        else:
            response.setdefault("message_for_user", f"No se pudo actualizar la familia.")
        return response
    except Exception as e:
        logger.error(f"Error en update_family: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al actualizar la familia: {str(e)}"
        }

def delete_family(tool_context, family_id: str):
    logger.info(f"TOOL EXECUTED: delete_family(family_id='{family_id}')")
    if not family_id:
        return {
            "status": "error",
            "message": "ID de la familia requerido.",
            "message_for_user": "Debes proporcionar el ID de la familia a eliminar."
        }
    try:
        api_result = make_fs_request("DELETE", f"/familias/{family_id}")
        if api_result.get("status") == "success":
            api_result.setdefault("message_for_user", f"Familia con ID '{family_id}' eliminada correctamente.")
        else:
            api_result.setdefault("message_for_user", f"No se pudo eliminar la familia con ID '{family_id}'.")
        return api_result
    except Exception as e:
        logger.error(f"Error en delete_family: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al eliminar la familia: {str(e)}"
        }

AGENT_TOOLS = [
    list_families,
    create_family,
    update_family,
    delete_family
]
