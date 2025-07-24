import logging
from typing import Optional, Any
from utils import make_fs_request

logger = logging.getLogger(__name__)

def list_manufacturers(tool_context):
    logger.info("TOOL EXECUTED: list_manufacturers()")
    try:
        api_result = make_fs_request("GET", "/fabricantes")
        if api_result.get("status") == "success":
            data = api_result.get("data", [])
            api_result.setdefault("message_for_user", f"Se encontraron {len(data)} fabricantes.")
        else:
            api_result.setdefault("message_for_user", "No se pudo obtener la lista de fabricantes.")
        return api_result
    except Exception as e:
        logger.error(f"Error en list_manufacturers: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al listar fabricantes: {str(e)}"
        }

def create_manufacturer(tool_context, nombre: str, **kwargs):
    logger.info(f"TOOL EXECUTED: create_manufacturer(nombre='{nombre}')")
    
    if not nombre:
        return {
            "status": "error",
            "message": "El nombre del fabricante es obligatorio.",
            "message_for_user": "Debes indicar el nombre del fabricante."
        }

    data = {"nombre": nombre}
    data.update(kwargs)

    try:
        response = make_fs_request("POST", "/fabricantes", data=data)
        if response.get("status") == "success":
            response.setdefault("message_for_user", f"Fabricante '{nombre}' creado correctamente.")
        else:
            response.setdefault("message_for_user", f"No se pudo crear el fabricante '{nombre}'.")
        return response
    except Exception as e:
        logger.error(f"Error en create_manufacturer: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al crear el fabricante: {str(e)}"
        }

def update_manufacturer(tool_context, id: str, **kwargs):
    logger.info(f"TOOL EXECUTED: update_manufacturer(id='{id}')")

    if not id:
        return {
            "status": "error",
            "message": "El ID del fabricante es obligatorio para actualizar.",
            "message_for_user": "Debes indicar el ID del fabricante a modificar."
        }

    if not kwargs:
        return {
            "status": "error",
            "message": "No se proporcionaron campos para actualizar.",
            "message_for_user": "Debes indicar al menos un campo para modificar del fabricante."
        }

    try:
        response = make_fs_request("PUT", f"/fabricantes/{id}", data=kwargs)
        if response.get("status") == "success":
            response.setdefault("message_for_user", f"Fabricante actualizado correctamente.")
        else:
            response.setdefault("message_for_user", f"No se pudo actualizar el fabricante.")
        return response
    except Exception as e:
        logger.error(f"Error en update_manufacturer: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al actualizar el fabricante: {str(e)}"
        }

def delete_manufacturer(tool_context, manufacturer_id: str):
    logger.info(f"TOOL EXECUTED: delete_manufacturer(manufacturer_id='{manufacturer_id}')")
    if not manufacturer_id:
        return {
            "status": "error",
            "message": "ID del fabricante requerido.",
            "message_for_user": "Debes proporcionar el ID del fabricante a eliminar."
        }
    try:
        api_result = make_fs_request("DELETE", f"/fabricantes/{manufacturer_id}")
        if api_result.get("status") == "success":
            api_result.setdefault("message_for_user", f"Fabricante con ID '{manufacturer_id}' eliminado correctamente.")
        else:
            api_result.setdefault("message_for_user", f"No se pudo eliminar el fabricante con ID '{manufacturer_id}'.")
        return api_result
    except Exception as e:
        logger.error(f"Error en delete_manufacturer: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al eliminar el fabricante: {str(e)}"
        }

AGENT_TOOLS = [
    create_manufacturer,
    update_manufacturer,
    delete_manufacturer,
    list_manufacturers
]