import logging
from typing import Any, Optional
from utils import make_fs_request
import re

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

def get_asiento(tool_context, asiento_input: str):
    """
    Obtiene información de uno o varios asientos según ID, concepto exacto o parcial.

    Args:
        asiento_input (str): ID del asiento o parte del concepto a buscar.
    """
    logger.info(f"TOOL EXECUTED: get_asiento(asiento_input='{asiento_input}')")

    def es_uuid(valor: str) -> bool:
        return re.fullmatch(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}", valor
        ) is not None

    try:
        if es_uuid(asiento_input):
            # Buscar directamente por ID
            api_result = make_fs_request("GET", f"/asientos/{asiento_input}")
            if api_result.get("status") == "success":
                asiento_data = api_result.get("data", {})
                if asiento_data:
                    return {
                        "status": "success",
                        "data": asiento_data,
                        "message_for_user": f"Asiento encontrado: '{asiento_data.get('concepto')}' (ID: {asiento_data.get('id')}, Número: {asiento_data.get('numero')})."
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Asiento no encontrado",
                        "message_for_user": f"No se encontró un asiento con ID '{asiento_input}'."
                    }

        # Buscar por concepto parcial o número de asiento
        all_result = make_fs_request("GET", "/asientos")
        if all_result.get("status") != "success":
            return {
                "status": "error",
                "message": "Error al obtener lista de asientos",
                "message_for_user": "No pude obtener la lista de asientos para buscar coincidencias."
            }

        asientos = all_result.get("data", [])
        coincidencias = [
            a for a in asientos if (
                asiento_input.lower() in (a.get("concepto") or "").lower() or
                asiento_input.lower() in (a.get("numero") or "").lower()
            )
        ]

        if len(coincidencias) == 1:
            asiento = coincidencias[0]
            return {
                "status": "success",
                "data": asiento,
                "message_for_user": f"Asiento encontrado: '{asiento.get('concepto')}' (Número: {asiento.get('numero')})."
            }
        elif len(coincidencias) > 1:
            return {
                "status": "multiple",
                "data": coincidencias,
                "message_for_user": f"Se encontraron {len(coincidencias)} asientos que coinciden con '{asiento_input}'. Por favor, especifica el ID o número exacto si es posible."
            }
        else:
            return {
                "status": "not_found",
                "message": "No hay coincidencias",
                "message_for_user": f"No se encontró ningún asiento que contenga '{asiento_input}' en su concepto o número."
            }

    except Exception as e:
        logger.error(f"Error al obtener asiento '{asiento_input}': {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al obtener el asiento '{asiento_input}': {str(e)}"
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


