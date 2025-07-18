import logging
from typing import Any, Optional
from utils import make_fs_request

logger = logging.getLogger(__name__)

# ----------- LIST -----------

def list_asientos(tool_context):
    """Lista todos los asientos disponibles en el sistema."""
    logger.info("TOOL EXECUTED: list_asientos()")
    try:
        api_result = make_fs_request("GET", "/asientos")
        if api_result.get("status") == "success":
            logger.info("Listado de asientos completado exitosamente")
            data = api_result.get("data", [])
            api_result.setdefault("message_for_user", f"Encontrados {len(data)} asientos.")
        else:
            logger.error(f"Error en listado de asientos: {api_result}")
            api_result.setdefault("message_for_user", "No pude obtener la lista de asientos.")
        return api_result
    except Exception as e:
        logger.error(f"Error al listar asientos: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al obtener la lista de asientos: {str(e)}"
        }

# ----------- GET -----------

def get_asiento(tool_context, asiento_id: str):
    """Obtiene un asiento específico por su ID."""
    logger.info(f"TOOL EXECUTED: get_asiento(asiento_id='{asiento_id}')")
    try:
        api_result = make_fs_request("GET", f"/asientos/{asiento_id}")
        if api_result.get("status") == "success":
            logger.info("Asiento obtenido correctamente")
            data = api_result.get("data", {})
            descripcion = data.get("concepto", "Sin concepto")
            api_result.setdefault("message_for_user", f"Asiento '{descripcion}' (ID: {asiento_id}) obtenido correctamente.")
        else:
            logger.error(f"Error obteniendo asiento: {api_result}")
            api_result.setdefault("message_for_user", f"No pude obtener el asiento con ID {asiento_id}.")
        return api_result
    except Exception as e:
        logger.error(f"Error al obtener asiento {asiento_id}: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al obtener el asiento {asiento_id}: {str(e)}"
        }

# ----------- UPSERT -----------

def upsert_asiento(tool_context, asiento_id: Optional[str] = None, **kwargs: Any) -> dict:
    """
    Crea o actualiza un asiento contable.
    Si se proporciona `asiento_id`, actualiza. Si no, crea.
    """
    logger.info(f"TOOL EXECUTED: upsert_asiento(asiento_id='{asiento_id}', kwargs={kwargs})")

    required_fields = [
        "canal", "codejercicio", "concepto", "documento", "editable",
        "fecha", "iddiario", "idempresa", "numero", "operacion"
    ]

    if not asiento_id:
        # Validar campos solo si es creación
        missing = [f for f in required_fields if f not in kwargs or kwargs[f] in [None, ""]]
        if missing:
            return {
                "status": "error",
                "message": f"Faltan campos obligatorios: {', '.join(missing)}",
                "message_for_user": f"Para crear un asiento necesito: {', '.join(missing)}"
            }

    # Defaults en ambos casos
    defaults = {
        "importe": 0
    }
    for k, v in defaults.items():
        kwargs.setdefault(k, v)

    method = "PUT" if asiento_id else "POST"
    endpoint = f"/asientos/{asiento_id}" if asiento_id else "/asientos"

    try:
        api_result = make_fs_request(method, endpoint, data=kwargs)
        if api_result.get("status") == "success":
            logger.info("Asiento creado/actualizado correctamente")
            accion = "actualizado" if asiento_id else "creado"
            concepto = kwargs.get("concepto", "sin concepto")
            api_result.setdefault("message_for_user", f"Asiento '{concepto}' {accion} correctamente.")
        else:
            logger.error(f"Error en upsert asiento: {api_result}")
            api_result.setdefault("message_for_user", f"No pude guardar el asiento. {api_result.get('message', '')}")
        return api_result
    except Exception as e:
        logger.error(f"Error en upsert asiento: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al guardar el asiento: {str(e)}"
        }

# ----------- DELETE -----------

def delete_asiento(tool_context, asiento_id: str) -> dict:
    """
    Elimina un asiento del sistema.
    """
    logger.info(f"TOOL EXECUTED: delete_asiento(asiento_id='{asiento_id}')")

    if not asiento_id:
        return {
            "status": "error",
            "message": "ID de asiento obligatorio",
            "message_for_user": "Necesito el ID del asiento para eliminarlo."
        }

    try:
        api_result = make_fs_request("DELETE", f"/asientos/{asiento_id}")
        if api_result.get("status") == "success":
            logger.info("Asiento eliminado correctamente")
            api_result.setdefault("message_for_user", f"Asiento con ID {asiento_id} eliminado correctamente.")
        else:
            logger.error(f"Error eliminando asiento: {api_result}")
            api_result.setdefault("message_for_user", f"No pude eliminar el asiento {asiento_id}.")
        return api_result
    except Exception as e:
        logger.error(f"Error eliminando asiento {asiento_id}: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al eliminar el asiento {asiento_id}: {str(e)}"
        }

# ----------- REGISTRO DE TOOLS -----------

ASIENTOS_TOOLS = [
    list_asientos,
    get_asiento,
    upsert_asiento,
    delete_asiento
]


