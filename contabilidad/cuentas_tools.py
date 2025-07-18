import logging
from typing import Any, Optional
from utils import make_fs_request

logger = logging.getLogger(__name__)

# ----------- LIST -----------

def list_cuentas(tool_context):
    """Lista todas las cuentas disponibles en el sistema."""
    logger.info("TOOL EXECUTED: list_cuentas()")
    try:
        api_result = make_fs_request("GET", "/cuentas")
        if api_result.get("status") == "success":
            logger.info("Listado de cuentas completado exitosamente")
            data = api_result.get("data", [])
            api_result.setdefault("message_for_user", f"Encontradas {len(data)} cuentas.")
        else:
            logger.error(f"Error en listado de cuentas: {api_result}")
            api_result.setdefault("message_for_user", "No pude obtener la lista de cuentas.")
        return api_result
    except Exception as e:
        logger.error(f"Error al listar cuentas: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al obtener la lista de cuentas: {str(e)}"
        }

# ----------- GET -----------

def get_cuenta(tool_context, cuenta_id: str):
    """Obtiene una cuenta específica por su ID."""
    logger.info(f"TOOL EXECUTED: get_cuenta(cuenta_id='{cuenta_id}')")
    try:
        api_result = make_fs_request("GET", f"/cuentas/{cuenta_id}")
        if api_result.get("status") == "success":
            logger.info("Cuenta obtenida correctamente")
            data = api_result.get("data", {})
            descripcion = data.get("descripcion", "Sin descripción")
            api_result.setdefault("message_for_user", f"Cuenta '{descripcion}' (ID: {cuenta_id}) obtenida correctamente.")
        else:
            logger.error(f"Error obteniendo cuenta: {api_result}")
            api_result.setdefault("message_for_user", f"No pude obtener la cuenta con ID {cuenta_id}.")
        return api_result
    except Exception as e:
        logger.error(f"Error al obtener cuenta {cuenta_id}: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al obtener la cuenta {cuenta_id}: {str(e)}"
        }

# ----------- UPSERT -----------

def upsert_cuenta(tool_context, cuenta_id: Optional[str] = None, **kwargs: Any) -> dict:
    """
    Crea o actualiza una cuenta contable.
    Si se proporciona `cuenta_id`, actualiza. Si no, crea.
    """
    logger.info(f"TOOL EXECUTED: upsert_cuenta(cuenta_id='{cuenta_id}', kwargs={kwargs})")

    required_fields = [
        "codcuenta", "codcuentaesp", "codejercicio", "debe", "descripcion",
        "haber", "parent_codcuenta", "parent_idcuenta", "saldo"
    ]

    if not cuenta_id:
        # Validar campos solo si es creación
        missing = [f for f in required_fields if f not in kwargs or kwargs[f] in [None, ""]]
        if missing:
            return {
                "status": "error",
                "message": f"Faltan campos obligatorios: {', '.join(missing)}",
                "message_for_user": f"Para crear una cuenta necesito: {', '.join(missing)}"
            }

    # Defaults en ambos casos (si es necesario)
    # defaults = {}
    # for k, v in defaults.items():
    #     kwargs.setdefault(k, v)

    method = "PUT" if cuenta_id else "POST"
    endpoint = f"/cuentas/{cuenta_id}" if cuenta_id else "/cuentas"

    try:
        api_result = make_fs_request(method, endpoint, data=kwargs)
        if api_result.get("status") == "success":
            logger.info("Cuenta creada/actualizada correctamente")
            accion = "actualizada" if cuenta_id else "creada"
            descripcion = kwargs.get("descripcion", "sin descripción")
            api_result.setdefault("message_for_user", f"Cuenta '{descripcion}' {accion} correctamente.")
        else:
            logger.error(f"Error en upsert cuenta: {api_result}")
            api_result.setdefault("message_for_user", f"No pude guardar la cuenta. {api_result.get('message', '')}")
        return api_result
    except Exception as e:
        logger.error(f"Error en upsert cuenta: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al guardar la cuenta: {str(e)}"
        }

# ----------- DELETE -----------

def delete_cuenta(tool_context, cuenta_id: str) -> dict:
    """
    Elimina una cuenta del sistema.
    """
    logger.info(f"TOOL EXECUTED: delete_cuenta(cuenta_id='{cuenta_id}')")

    if not cuenta_id:
        return {
            "status": "error",
            "message": "ID de cuenta obligatorio",
            "message_for_user": "Necesito el ID de la cuenta para eliminarla."
        }

    try:
        api_result = make_fs_request("DELETE", f"/cuentas/{cuenta_id}")
        if api_result.get("status") == "success":
            logger.info("Cuenta eliminada correctamente")
            api_result.setdefault("message_for_user", f"Cuenta con ID {cuenta_id} eliminada correctamente.")
        else:
            logger.error(f"Error eliminando cuenta: {api_result}")
            api_result.setdefault("message_for_user", f"No pude eliminar la cuenta {cuenta_id}.")
        return api_result
    except Exception as e:
        logger.error(f"Error eliminando cuenta {cuenta_id}: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al eliminar la cuenta {cuenta_id}: {str(e)}"
        }

# ----------- REGISTRO DE TOOLS -----------

CUENTAS_TOOLS = [
    list_cuentas,
    get_cuenta,
    upsert_cuenta,
    delete_cuenta
]