import logging
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

def get_forma_pago(tool_context, forma_id: str):
    """Obtiene una forma de pago específica por su ID."""
    logger.info(f"TOOL EXECUTED: get_forma_pago(forma_id='{forma_id}')")
    try:
        api_result = make_fs_request("GET", f"/formapagos/{forma_id}")
        if api_result.get("status") == "success":
            logger.info("Forma de pago obtenida correctamente")
            data = api_result.get("data", {})
            descripcion = data.get("descripcion", "Sin descripción")
            api_result.setdefault("message_for_user", f"Forma de pago '{descripcion}' (ID: {forma_id}) obtenida correctamente.")
        else:
            logger.error(f"Error obteniendo forma de pago: {api_result}")
            api_result.setdefault("message_for_user", f"No pude obtener la forma de pago con ID {forma_id}.")
        return api_result
    except Exception as e:
        logger.error(f"Error al obtener forma de pago {forma_id}: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al obtener la forma de pago {forma_id}: {str(e)}"
        }

# ----------- UPSERT -----------

def upsert_forma_pago(tool_context, forma_id: Optional[str] = None, **kwargs: Any) -> dict:
    """
    Crea o actualiza una forma de pago.
    Si se proporciona `forma_id`, actualiza. Si no, crea.
    """
    logger.info(f"TOOL EXECUTED: upsert_forma_pago(forma_id='{forma_id}', kwargs={kwargs})")

    required_fields = [
        "codcuentabanco", "descripcion", "domiciliado", "idempresa",
        "plazovencimiento", "tipovencimiento"
    ]

    if not forma_id:
        # Validar campos solo si es creación
        missing = [f for f in required_fields if f not in kwargs or kwargs[f] in [None, ""]]
        if missing:
            return {
                "status": "error",
                "message": f"Faltan campos obligatorios: {', '.join(missing)}",
                "message_for_user": f"Para crear una forma de pago necesito: {', '.join(missing)}"
            }

    # Defaults en ambos casos
    defaults = {
        "activa": True,
        "imprimir": True,
        "pagado": False
    }
    for k, v in defaults.items():
        kwargs.setdefault(k, v)

    method = "PUT" if forma_id else "POST"
    endpoint = f"/formapagos/{forma_id}" if forma_id else "/formapagos"

    try:
        api_result = make_fs_request(method, endpoint, data=kwargs)
        if api_result.get("status") == "success":
            logger.info("Forma de pago creada/actualizada correctamente")
            accion = "actualizada" if forma_id else "creada"
            descripcion = kwargs.get("descripcion", "sin descripción")
            api_result.setdefault("message_for_user", f"Forma de pago '{descripcion}' {accion} correctamente.")
        else:
            logger.error(f"Error en upsert forma de pago: {api_result}")
            api_result.setdefault("message_for_user", f"No pude guardar la forma de pago. {api_result.get('message', '')}")
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
