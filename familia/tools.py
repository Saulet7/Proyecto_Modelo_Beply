import logging
import json
from typing import Optional, Any
from utils import make_fs_request
import re

logger = logging.getLogger(__name__)

def list_familias(tool_context):
    logger.info("TOOL EXECUTED: list_familias()")
    try:
        api_result = make_fs_request("GET", "/familias")

        if api_result.get("status") == "success":
            familias_data = api_result.get("data", [])
            if "message_for_user" not in api_result:
                api_result["message_for_user"] = f"Encontradas {len(familias_data)} familias en el sistema."
            return api_result
        else:
            if "message_for_user" not in api_result:
                api_result["message_for_user"] = f"No pude obtener la lista de familias. Error: {api_result.get('message', 'desconocido')}"
            return api_result

    except Exception as e:
        logger.error(f"Error al listar familias: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al obtener la lista de familias: {str(e)}"
        }

def get_familia(tool_context, familia_id: str):
    logger.info(f"TOOL EXECUTED: get_familia(familia_id='{familia_id}')")

    try:
        api_result = make_fs_request("GET", f"/familias/{familia_id}")
        if api_result.get("status") == "success":
            familia = api_result.get("data", {})
            # productos se espera entero
            productos = familia.get("productos")
            if not isinstance(productos, int):
                productos = 0
            return {
                "status": "success",
                "data": {
                    "idfamilia": familia.get("idfamilia"),
                    "codigo": familia.get("codigo"),
                    "descripcion": familia.get("descripcion"),
                    "padre": familia.get("padre"),
                    "productos": productos,
                    "status": "found"
                },
                "message_for_user": f"Familia encontrada: '{familia.get('descripcion')}' (ID: {familia.get('idfamilia')})."
            }
        else:
            return {
                "status": "error",
                "message": "Familia no encontrada",
                "message_for_user": f"No se encontró una familia con ID '{familia_id}'."
            }

    except Exception as e:
        logger.error(f"Error al obtener familia '{familia_id}': {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al obtener la familia '{familia_id}': {str(e)}"
        }

def create_familia(tool_context, codigo: str, descripcion: str, padre: Optional[str] = None, productos: Optional[int] = 0, **kwargs: Any):
    logger.info(f"TOOL EXECUTED: create_familia(codigo='{codigo}', descripcion='{descripcion}', padre='{padre}', productos={productos}, kwargs={kwargs})")

    if not codigo or not descripcion:
        return {
            "status": "error",
            "message": "Código y descripción son obligatorios.",
            "message_for_user": "Necesito el código y la descripción de la familia para poder crearla."
        }

    # aseguramos que productos sea entero no negativo
    if not isinstance(productos, int) or productos < 0:
        productos = 0

    form_data = {
        "codigo": codigo,
        "descripcion": descripcion,
        "productos": productos
    }

    # Solo añadimos padre si es un string no vacío
    if padre and isinstance(padre, str) and padre.strip() != "":
        form_data["padre"] = padre.strip()
    else:
        form_data["padre"] = None

    form_data.update(kwargs)

    api_result = make_fs_request("POST", "/familias", data=form_data)

    if api_result.get("status") == "success" and "message_for_user" not in api_result:
        creado = api_result.get("data", {})
        api_result["message_for_user"] = f"¡Familia '{descripcion}' creada con éxito! (ID: {creado.get('idfamilia')})"
    elif api_result.get("status") == "error" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"No pude crear la familia '{descripcion}'. Error: {api_result.get('message', 'desconocido')}"

    return api_result

def update_familia(tool_context, familia_id: str, **kwargs: Any):
    logger.info(f"TOOL EXECUTED: update_familia(familia_id='{familia_id}', kwargs={kwargs})")

    if not familia_id:
        return {
            "status": "error",
            "message": "ID de la familia es obligatorio.",
            "message_for_user": "Necesito el ID de la familia para poder actualizarla."
        }

    if not kwargs:
        return {
            "status": "error",
            "message": "No hay datos para actualizar.",
            "message_for_user": "No has proporcionado ningún dato para actualizar."
        }

    clean_data = {}
    for k, v in kwargs.items():
        if v is None:
            continue
        if isinstance(v, str) and v.strip() == "":
            continue
        if k == "productos":
            # aseguramos que productos sea entero no negativo
            if isinstance(v, int) and v >= 0:
                clean_data[k] = v
            else:
                logger.warning(f"Ignorando valor inválido para productos: {v}")
        else:
            clean_data[k] = v

    if not clean_data:
        return {
            "status": "error",
            "message": "No hay datos válidos para actualizar después de limpieza.",
            "message_for_user": "Los datos proporcionados para actualizar no son válidos."
        }

    api_result = make_fs_request("PUT", f"/familias/{familia_id}", data=clean_data)

    if api_result.get("status") == "success" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"Familia con ID {familia_id} actualizada exitosamente."
    elif api_result.get("status") == "error" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"No pude actualizar la familia con ID {familia_id}. Error: {api_result.get('message', 'desconocido')}"

    return api_result

def delete_familia(tool_context, familia_id: str):
    logger.info(f"TOOL EXECUTED: delete_familia(familia_id='{familia_id}')")

    if not familia_id:
        return {
            "status": "error",
            "message": "ID de la familia es obligatorio.",
            "message_for_user": "Necesito el ID de la familia para poder eliminarla."
        }

    api_result = make_fs_request("DELETE", f"/familias/{familia_id}")

    if api_result.get("status") == "success" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"Familia con ID {familia_id} eliminada exitosamente."
    elif api_result.get("status") == "error" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"No pude eliminar la familia con ID {familia_id}. Error: {api_result.get('message', 'desconocido')}"

    return api_result

FAMILIA_AGENT_TOOLS = [
    list_familias,
    get_familia,
    create_familia,
    update_familia,
    delete_familia
]

def setup_debug_logging():
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler = logging.FileHandler('familia_api_debug.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("Logging de debugging para FamiliaAgent configurado")

setup_debug_logging()
