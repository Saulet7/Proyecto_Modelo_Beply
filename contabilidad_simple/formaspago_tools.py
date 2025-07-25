import logging
import re
from typing import Any, Optional
from utils import make_fs_request

logger = logging.getLogger(__name__)

# ----------- LIST -----------

def list_formas_pago(tool_context):
    """Lista todas las formas de pago disponibles en el sistema."""
    logger.info("TOOL EXECUTED: list_formas_pago()")
    try:
        api_result = make_fs_request("GET", "/formapagos")
        if api_result.get("status") == "success":
            logger.info("Listado de formas de pago completado exitosamente")
            data = api_result.get("data", [])
            api_result.setdefault("message_for_user", f"Encontradas {len(data)} formas de pago.")
        else:
            logger.error(f"Error en listado de formas de pago: {api_result}")
            api_result.setdefault("message_for_user", "No pude obtener la lista de formas de pago.")
        return api_result
    except Exception as e:
        logger.error(f"Error al listar formas de pago: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al obtener la lista de formas de pago: {str(e)}"
        }

# ----------- GET -----------

def get_forma_pago(tool_context, forma_input: str):
    """
    Obtiene información de una o varias formas de pago según ID o descripción.

    Args:
        forma_input (str): ID de la forma de pago o parte de la descripción a buscar.
    """
    logger.info(f"TOOL EXECUTED: get_forma_pago(forma_input='{forma_input}')")

    def es_uuid(valor: str) -> bool:
        return re.fullmatch(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}", valor
        ) is not None

    try:
        if es_uuid(forma_input):
            # Buscar directamente por ID
            api_result = make_fs_request("GET", f"/formapagos/{forma_input}")
            if api_result.get("status") == "success":
                forma_data = api_result.get("data", {})
                if forma_data:
                    return {
                        "status": "success",
                        "data": forma_data,
                        "message_for_user": f"Forma de pago encontrada: '{forma_data.get('descripcion')}' (Plazo: {forma_data.get('plazovencimiento')} días)."
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Forma de pago no encontrada",
                        "message_for_user": f"No se encontró una forma de pago con ID '{forma_input}'."
                    }

        # Buscar por descripción
        all_result = make_fs_request("GET", "/formapagos")
        if all_result.get("status") != "success":
            return {
                "status": "error",
                "message": "Error al obtener lista de formas de pago",
                "message_for_user": "No pude obtener la lista de formas de pago para buscar coincidencias."
            }

        formas_pago = all_result.get("data", [])
        coincidencias = [
            f for f in formas_pago if (
                forma_input.lower() in (f.get("descripcion") or "").lower()
            )
        ]

        if len(coincidencias) == 1:
            forma = coincidencias[0]
            return {
                "status": "success",
                "data": forma,
                "message_for_user": f"Forma de pago encontrada: '{forma.get('descripcion')}' (Plazo: {forma.get('plazovencimiento')} días)."
            }
        elif len(coincidencias) > 1:
            return {
                "status": "multiple",
                "data": coincidencias,
                "message_for_user": f"Se encontraron {len(coincidencias)} formas de pago que coinciden con '{forma_input}'. Por favor, especifica la descripción exacta o ID si es posible."
            }
        else:
            return {
                "status": "not_found",
                "message": "No hay coincidencias",
                "message_for_user": f"No se encontró ninguna forma de pago que contenga '{forma_input}' en su descripción."
            }

    except Exception as e:
        logger.error(f"Error al obtener forma de pago '{forma_input}': {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al obtener la forma de pago '{forma_input}': {str(e)}"
        }

# ----------- UPSERT -----------

def upsert_forma_pago(tool_context, forma_id: Optional[str] = None, **kwargs: Any) -> dict:
    """
    Crea o actualiza una forma de pago.
    Si se proporciona `forma_id`, actualiza. Si no, crea.
    
    Los únicos campos realmente obligatorios son:
    - descripcion: Nombre descriptivo de la forma de pago (ej. "Tarjeta de crédito")
    - idempresa: ID de la empresa
    
    El resto se rellenará con valores por defecto.
    """
    logger.info(f"TOOL EXECUTED: upsert_forma_pago(forma_id='{forma_id}', kwargs={kwargs})")

    # Campos mínimos realmente necesarios
    required_fields = ["descripcion", "idempresa"]

    if not forma_id:
        # Validar solo los campos mínimos si es creación
        missing = [f for f in required_fields if f not in kwargs or kwargs[f] in [None, ""]]
        if missing:
            return {
                "status": "error",
                "message": f"Faltan campos obligatorios: {', '.join(missing)}",
                "message_for_user": f"Para crear una forma de pago necesito como mínimo: {', '.join(missing)}"
            }
    
    # Valores por defecto para simplificar la creación
    defaults = {
        "activa": True,              # Activa por defecto
        "codcuentabanco": "",        # Sin cuenta bancaria específica
        "codpago": "",               # Código de pago autogenerado
        "domiciliado": False,        # No domiciliado por defecto
        "imprimir": True,            # Se puede imprimir por defecto
        "pagado": False,             # No marcado como pagado por defecto
        "plazovencimiento": 0,       # Plazo de vencimiento inmediato por defecto
        "tipovencimiento": "dias"    # Tipo de vencimiento en días por defecto
    }
    
    # Aplicar defaults sólo para los campos que faltan
    for k, v in defaults.items():
        kwargs.setdefault(k, v)

    method = "PUT" if forma_id else "POST"
    endpoint = f"/formaspago/{forma_id}" if forma_id else "/formaspago"

    try:
        api_result = make_fs_request(method, endpoint, data=kwargs)
        if api_result.get("status") == "success":
            logger.info("Forma de pago creada/actualizada correctamente")
            accion = "actualizada" if forma_id else "creada"
            descripcion = kwargs.get("descripcion", "sin descripción")
            plazo_info = ""
            if kwargs.get("plazovencimiento") and kwargs.get("plazovencimiento") > 0:
                plazo_info = f" con plazo de {kwargs.get('plazovencimiento')} {kwargs.get('tipovencimiento', 'días')}"
            
            api_result.setdefault("message_for_user", 
                               f"Forma de pago '{descripcion}'{plazo_info} {accion} correctamente.")
        else:
            logger.error(f"Error en upsert forma de pago: {api_result}")
            api_result.setdefault("message_for_user", 
                               f"No pude guardar la forma de pago. {api_result.get('message', '')}")
        return api_result
    except Exception as e:
        logger.error(f"Error en upsert forma de pago: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al guardar la forma de pago: {str(e)}"
        }

# ----------- DELETE -----------

def delete_forma_pago(tool_context, forma_id: str) -> dict:
    """
    Elimina una forma de pago del sistema.
    """
    logger.info(f"TOOL EXECUTED: delete_forma_pago(forma_id='{forma_id}')")

    if not forma_id:
        return {
            "status": "error",
            "message": "ID de forma de pago obligatorio",
            "message_for_user": "Necesito el ID de la forma de pago para eliminarla."
        }

    try:
        api_result = make_fs_request("DELETE", f"/formapagos/{forma_id}")
        if api_result.get("status") == "success":
            logger.info("Forma de pago eliminada correctamente")
            api_result.setdefault("message_for_user", f"Forma de pago con ID {forma_id} eliminada correctamente.")
        else:
            logger.error(f"Error eliminando forma de pago: {api_result}")
            api_result.setdefault("message_for_user", f"No pude eliminar la forma de pago {forma_id}.")
        return api_result
    except Exception as e:
        logger.error(f"Error eliminando forma de pago {forma_id}: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al eliminar la forma de pago {forma_id}: {str(e)}"
        }

# ----------- REGISTRO DE TOOLS -----------

FORMASPAGO_TOOLS = [
    list_formas_pago,
    get_forma_pago,
    upsert_forma_pago,
    delete_forma_pago
]
