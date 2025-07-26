import logging
from typing import Optional, Any
from utils import make_fs_request

logger = logging.getLogger(__name__)

def list_carriers(tool_context, **filters):
    logger.info(f"TOOL EXECUTED: list_carriers(filters={filters})")
    try:
        api_result = make_fs_request("GET", "/agenciatransportes", params=filters)
        if api_result.get("status") == "success":
            data = api_result.get("data", [])
            api_result.setdefault("message_for_user", f"Se encontraron {len(data)} transportistas.")
        else:
            api_result.setdefault("message_for_user", "No se pudo obtener la lista de transportistas.")
        return api_result
    except Exception as e:
        logger.error(f"Error en list_carriers: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al listar transportistas: {str(e)}"
        }

def create_carrier(tool_context, nombre: str, codigo: str, telefono: str, web: str = "", activo: bool = True):
    logger.info(f"TOOL EXECUTED: create_carrier(nombre='{nombre}', codigo='{codigo}')")

    # Validación de campos obligatorios
    if not nombre or not codigo or not telefono:
        return {
            "status": "error",
            "message": "Faltan campos obligatorios: nombre, código o teléfono.",
            "message_for_user": "Debes indicar al menos el nombre, código y teléfono del transportista."
        }

    data = {
        "nombre": nombre,
        "codigo": codigo,
        "telefono": telefono,
        "web": web,
        "activo": int(activo)
    }

    try:
        api_result = make_fs_request("POST", "/agenciatransportes", data=data)
        if api_result.get("status") == "success":
            api_result.setdefault("message_for_user", f"Transportista '{nombre}' creado correctamente.")
        else:
            api_result.setdefault("message_for_user", f"No se pudo crear el transportista '{nombre}'.")
        return api_result
    except Exception as e:
        logger.error(f"Error en create_carrier: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al crear el transportista: {str(e)}"
        }

def update_carrier(tool_context, id: str, **kwargs):
    logger.info(f"TOOL EXECUTED: update_carrier(id='{id}', cambios={kwargs})")

    if not id:
        return {
            "status": "error",
            "message": "El ID del transportista es obligatorio.",
            "message_for_user": "Debes indicar el ID del transportista que deseas modificar."
        }

    # Filtrar los campos válidos para actualizar
    campos_validos = ["nombre", "codigo", "web", "telefono", "activo"]
    data = {k: v for k, v in kwargs.items() if k in campos_validos}

    if not data:
        return {
            "status": "error",
            "message": "No se proporcionaron campos válidos para actualizar.",
            "message_for_user": "Debes indicar al menos un campo válido para modificar."
        }

    # Convertir booleanos a enteros si es necesario
    if "activo" in data and isinstance(data["activo"], bool):
        data["activo"] = int(data["activo"])

    try:
        api_result = make_fs_request("PUT", f"/agenciatransportes/{id}", data=data)
        if api_result.get("status") == "success":
            api_result.setdefault("message_for_user", f"Transportista actualizado correctamente.")
        else:
            api_result.setdefault("message_for_user", f"No se pudo actualizar el transportista con ID '{id}'.")
        return api_result
    except Exception as e:
        logger.error(f"Error en update_carrier: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al actualizar el transportista: {str(e)}"
        }

def delete_carrier(tool_context, carrier_id: str):
    logger.info(f"TOOL EXECUTED: delete_carrier(carrier_id='{carrier_id}')")
    if not carrier_id:
        return {
            "status": "error",
            "message": "ID del transportista requerido.",
            "message_for_user": "Debes proporcionar el ID del transportista a eliminar."
        }
    try:
        api_result = make_fs_request("DELETE", f"/agenciatransportes/{carrier_id}")
        if api_result.get("status") == "success":
            api_result.setdefault("message_for_user", f"Transportista con ID '{carrier_id}' eliminado correctamente.")
        else:
            api_result.setdefault("message_for_user", f"No se pudo eliminar el transportista con ID '{carrier_id}'.")
        return api_result
    except Exception as e:
        logger.error(f"Error en delete_carrier: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al eliminar el transportista: {str(e)}"
        }

AGENT_TOOLS = [
    list_carriers,
    create_carrier,
    update_carrier,
    delete_carrier
]
