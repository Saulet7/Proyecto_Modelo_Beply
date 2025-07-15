import logging
import json
from typing import Optional, Any
from utils import make_fs_request
import re

logger = logging.getLogger(__name__)

def list_fabricantes(tool_context):
    logger.info("TOOL EXECUTED: list_fabricantes()")
    try:
        api_result = make_fs_request("GET", "/fabricantes")

        if api_result.get("status") == "success":
            fabricantes_data = api_result.get("data", [])
            if "message_for_user" not in api_result:
                api_result["message_for_user"] = f"Encontrados {len(fabricantes_data)} fabricantes en el sistema."
            return api_result
        else:
            if "message_for_user" not in api_result:
                api_result["message_for_user"] = f"No pude obtener la lista de fabricantes. Error: {api_result.get('message', 'desconocido')}"
            return api_result

    except Exception as e:
        logger.error(f"Error al listar fabricantes: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al obtener la lista de fabricantes: {str(e)}"
        }

def get_fabricante(tool_context, fabricante_id: str):
    logger.info(f"TOOL EXECUTED: get_fabricante(fabricante_id='{fabricante_id}')")

    try:
        api_result = make_fs_request("GET", f"/fabricantes/{fabricante_id}")
        if api_result.get("status") == "success":
            fabricante = api_result.get("data", {})
            return {
                "status": "success",
                "data": {
                    "idfabricante": fabricante.get("idfabricante"),
                    "nombre": fabricante.get("nombre"),
                    "status": "found"
                },
                "message_for_user": f"Fabricante encontrado: '{fabricante.get('nombre')}' (ID: {fabricante.get('idfabricante')})."
            }
        else:
            return {
                "status": "error",
                "message": "Fabricante no encontrado",
                "message_for_user": f"No se encontró un fabricante con ID '{fabricante_id}'."
            }

    except Exception as e:
        logger.error(f"Error al obtener fabricante '{fabricante_id}': {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al obtener el fabricante '{fabricante_id}': {str(e)}"
        }

def create_fabricante(tool_context, nombre: str, **kwargs: Any):
    logger.info(f"TOOL EXECUTED: create_fabricante(nombre='{nombre}', kwargs={kwargs})")

    if not nombre:
        return {
            "status": "error",
            "message": "El nombre del fabricante es obligatorio.",
            "message_for_user": "Necesito el nombre del fabricante para poder crearlo."
        }

    form_data = {"nombre": nombre}
    form_data.update(kwargs)

    api_result = make_fs_request("POST", "/fabricantes", data=form_data)

    if api_result.get("status") == "success" and "message_for_user" not in api_result:
        creado = api_result.get("data", {})
        api_result["message_for_user"] = f"¡Fabricante '{nombre}' creado con éxito! (ID: {creado.get('idfabricante')})"
    elif api_result.get("status") == "error" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"No pude crear el fabricante '{nombre}'. Error: {api_result.get('message', 'desconocido')}"

    return api_result

def update_fabricante(tool_context, fabricante_id: str, **kwargs: Any):
    logger.info(f"TOOL EXECUTED: update_fabricante(fabricante_id='{fabricante_id}', kwargs={kwargs})")

    if not fabricante_id:
        return {
            "status": "error",
            "message": "ID del fabricante es obligatorio.",
            "message_for_user": "Necesito el ID del fabricante para poder actualizarlo."
        }

    if not kwargs:
        return {
            "status": "error",
            "message": "No hay datos para actualizar.",
            "message_for_user": "No has proporcionado ningún dato para actualizar."
        }

    api_result = make_fs_request("PUT", f"/fabricantes/{fabricante_id}", data=kwargs)

    if api_result.get("status") == "success" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"Fabricante con ID {fabricante_id} actualizado exitosamente."
    elif api_result.get("status") == "error" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"No pude actualizar el fabricante con ID {fabricante_id}. Error: {api_result.get('message', 'desconocido')}"

    return api_result

def delete_fabricante(tool_context, fabricante_id: str):
    logger.info(f"TOOL EXECUTED: delete_fabricante(fabricante_id='{fabricante_id}')")

    if not fabricante_id:
        return {
            "status": "error",
            "message": "ID del fabricante es obligatorio.",
            "message_for_user": "Necesito el ID del fabricante para poder eliminarlo."
        }

    api_result = make_fs_request("DELETE", f"/fabricantes/{fabricante_id}")

    if api_result.get("status") == "success" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"Fabricante con ID {fabricante_id} eliminado exitosamente."
    elif api_result.get("status") == "error" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"No pude eliminar el fabricante con ID {fabricante_id}. Error: {api_result.get('message', 'desconocido')}"

    return api_result

FABRICANTE_AGENT_TOOLS = [
    list_fabricantes,
    get_fabricante,
    create_fabricante,
    update_fabricante,
    delete_fabricante
]

def setup_debug_logging():
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler = logging.FileHandler('fabricante_api_debug.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("Logging de debugging para FabricanteAgent configurado")

setup_debug_logging()