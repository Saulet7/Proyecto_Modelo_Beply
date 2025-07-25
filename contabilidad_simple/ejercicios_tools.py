import logging
from typing import Any, Optional
from utils import make_fs_request
import re

logger = logging.getLogger(__name__)

# ----------- LIST -----------

def list_ejercicios(tool_context):
    """Lista todos los ejercicios disponibles en el sistema."""
    logger.info("TOOL EXECUTED: list_ejercicios()")
    try:
        api_result = make_fs_request("GET", "/ejercicios")
        if api_result.get("status") == "success":
            logger.info("Listado de ejercicios completado exitosamente")
            data = api_result.get("data", [])
            api_result.setdefault("message_for_user", f"Encontrados {len(data)} ejercicios.")
        else:
            logger.error(f"Error en listado de ejercicios: {api_result}")
            api_result.setdefault("message_for_user", "No pude obtener la lista de ejercicios.")
        return api_result
    except Exception as e:
        logger.error(f"Error al listar ejercicios: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al obtener la lista de ejercicios: {str(e)}"
        }

# ----------- GET -----------

def get_ejercicio(tool_context, ejercicio_input: str):
    """
    Obtiene información de uno o varios ejercicios según ID, nombre o año.

    Args:
        ejercicio_input (str): ID del ejercicio, nombre o año a buscar.
    """
    logger.info(f"TOOL EXECUTED: get_ejercicio(ejercicio_input='{ejercicio_input}')")

    def es_uuid(valor: str) -> bool:
        return re.fullmatch(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}", valor
        ) is not None

    try:
        if es_uuid(ejercicio_input):
            # Buscar directamente por ID
            api_result = make_fs_request("GET", f"/ejercicios/{ejercicio_input}")
            if api_result.get("status") == "success":
                ejercicio_data = api_result.get("data", {})
                if ejercicio_data:
                    return {
                        "status": "success",
                        "data": ejercicio_data,
                        "message_for_user": f"Ejercicio encontrado: '{ejercicio_data.get('nombre')}' (Periodo: {ejercicio_data.get('fechainicio')} a {ejercicio_data.get('fechafin')})."
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Ejercicio no encontrado",
                        "message_for_user": f"No se encontró un ejercicio con ID '{ejercicio_input}'."
                    }

        # Buscar por nombre o año
        all_result = make_fs_request("GET", "/ejercicios")
        if all_result.get("status") != "success":
            return {
                "status": "error",
                "message": "Error al obtener lista de ejercicios",
                "message_for_user": "No pude obtener la lista de ejercicios para buscar coincidencias."
            }

        ejercicios = all_result.get("data", [])
        coincidencias = [
            e for e in ejercicios if (
                ejercicio_input.lower() in (e.get("nombre") or "").lower() or
                ejercicio_input in (e.get("fechainicio") or "") or
                ejercicio_input in (e.get("fechafin") or "")
            )
        ]

        if len(coincidencias) == 1:
            ejercicio = coincidencias[0]
            return {
                "status": "success",
                "data": ejercicio,
                "message_for_user": f"Ejercicio encontrado: '{ejercicio.get('nombre')}' (Periodo: {ejercicio.get('fechainicio')} a {ejercicio.get('fechafin')})."
            }
        elif len(coincidencias) > 1:
            return {
                "status": "multiple",
                "data": coincidencias,
                "message_for_user": f"Se encontraron {len(coincidencias)} ejercicios que coinciden con '{ejercicio_input}'. Por favor, especifica el nombre exacto o ID si es posible."
            }
        else:
            return {
                "status": "not_found",
                "message": "No hay coincidencias",
                "message_for_user": f"No se encontró ningún ejercicio que contenga '{ejercicio_input}' en su nombre o fechas."
            }

    except Exception as e:
        logger.error(f"Error al obtener ejercicio '{ejercicio_input}': {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al obtener el ejercicio '{ejercicio_input}': {str(e)}"
        }

# ----------- UPSERT -----------

def upsert_ejercicio(tool_context, ejercicio_id: Optional[str] = None, **kwargs: Any) -> dict:
    """
    Crea o actualiza un ejercicio contable.
    Si se proporciona `ejercicio_id`, actualiza. Si no, crea.
    
    Los únicos campos realmente obligatorios son:
    - nombre: Nombre del ejercicio (ej. "Ejercicio 2025")
    - fechainicio: Fecha de inicio (formato YYYY-MM-DD)
    - fechafin: Fecha de fin (formato YYYY-MM-DD)
    - idempresa: ID de la empresa
    
    El resto se rellenará con valores por defecto.
    """
    logger.info(f"TOOL EXECUTED: upsert_ejercicio(ejercicio_id='{ejercicio_id}', kwargs={kwargs})")

    # Campos mínimos realmente necesarios
    required_fields = ["nombre", "fechainicio", "fechafin", "idempresa"]

    if not ejercicio_id:
        # Validar solo los campos mínimos si es creación
        missing = [f for f in required_fields if f not in kwargs or kwargs[f] in [None, ""]]
        if missing:
            return {
                "status": "error",
                "message": f"Faltan campos obligatorios: {', '.join(missing)}",
                "message_for_user": f"Para crear un ejercicio necesito como mínimo: {', '.join(missing)}"
            }
    
    # Valores por defecto para simplificar la creación
    defaults = {
        "estado": "abierto",       # Estado por defecto: abierto
        "longsubcuenta": 10,       # Longitud estándar de subcuenta
    }
    
    # Aplicar defaults sólo para los campos que faltan
    for k, v in defaults.items():
        kwargs.setdefault(k, v)

    method = "PUT" if ejercicio_id else "POST"
    endpoint = f"/ejercicios/{ejercicio_id}" if ejercicio_id else "/ejercicios"

    try:
        api_result = make_fs_request(method, endpoint, data=kwargs)
        if api_result.get("status") == "success":
            logger.info("Ejercicio creado/actualizado correctamente")
            accion = "actualizado" if ejercicio_id else "creado"
            nombre = kwargs.get("nombre", "sin nombre")
            periodo = f"({kwargs.get('fechainicio')} a {kwargs.get('fechafin')})"
            api_result.setdefault("message_for_user", 
                               f"Ejercicio '{nombre}' {periodo} {accion} correctamente.")
        else:
            logger.error(f"Error en upsert ejercicio: {api_result}")
            api_result.setdefault("message_for_user", 
                               f"No pude guardar el ejercicio. {api_result.get('message', '')}")
        return api_result
    except Exception as e:
        logger.error(f"Error en upsert ejercicio: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al guardar el ejercicio: {str(e)}"
        }

# ----------- DELETE -----------

def delete_ejercicio(tool_context, ejercicio_id: str) -> dict:
    """
    Elimina un ejercicio del sistema.
    """
    logger.info(f"TOOL EXECUTED: delete_ejercicio(ejercicio_id='{ejercicio_id}')")

    if not ejercicio_id:
        return {
            "status": "error",
            "message": "ID de ejercicio obligatorio",
            "message_for_user": "Necesito el ID del ejercicio para eliminarlo."
        }

    try:
        api_result = make_fs_request("DELETE", f"/ejercicios/{ejercicio_id}")
        if api_result.get("status") == "success":
            logger.info("Ejercicio eliminado correctamente")
            api_result.setdefault("message_for_user", f"Ejercicio con ID {ejercicio_id} eliminado correctamente.")
        else:
            logger.error(f"Error eliminando ejercicio: {api_result}")
            api_result.setdefault("message_for_user", f"No pude eliminar el ejercicio {ejercicio_id}.")
        return api_result
    except Exception as e:
        logger.error(f"Error eliminando ejercicio {ejercicio_id}: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al eliminar el ejercicio {ejercicio_id}: {str(e)}"
        }

# ----------- REGISTRO DE TOOLS -----------

EJERCICIOS_TOOLS = [
    list_ejercicios,
    get_ejercicio,
    upsert_ejercicio,
    delete_ejercicio
]
