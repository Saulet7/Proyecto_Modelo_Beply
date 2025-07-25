import logging
from typing import Any, Optional
from utils import make_fs_request
import re

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

def get_cuenta(tool_context, cuenta_input: str):
    """
    Obtiene información de una o varias cuentas según ID, código o descripción.

    Args:
        cuenta_input (str): ID de la cuenta, código o parte de la descripción a buscar.
    """
    logger.info(f"TOOL EXECUTED: get_cuenta(cuenta_input='{cuenta_input}')")

    def es_uuid(valor: str) -> bool:
        return re.fullmatch(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}", valor
        ) is not None

    try:
        if es_uuid(cuenta_input):
            # Buscar directamente por ID
            api_result = make_fs_request("GET", f"/cuentas/{cuenta_input}")
            if api_result.get("status") == "success":
                cuenta_data = api_result.get("data", {})
                if cuenta_data:
                    return {
                        "status": "success",
                        "data": cuenta_data,
                        "message_for_user": f"Cuenta encontrada: '{cuenta_data.get('descripcion')}' (Código: {cuenta_data.get('codcuenta')})."
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Cuenta no encontrada",
                        "message_for_user": f"No se encontró una cuenta con ID '{cuenta_input}'."
                    }

        # Buscar por código o descripción
        all_result = make_fs_request("GET", "/cuentas")
        if all_result.get("status") != "success":
            return {
                "status": "error",
                "message": "Error al obtener lista de cuentas",
                "message_for_user": "No pude obtener la lista de cuentas para buscar coincidencias."
            }

        cuentas = all_result.get("data", [])
        coincidencias = [
            c for c in cuentas if (
                cuenta_input.lower() in (c.get("descripcion") or "").lower() or
                cuenta_input.lower() in (c.get("codcuenta") or "").lower()
            )
        ]

        if len(coincidencias) == 1:
            cuenta = coincidencias[0]
            return {
                "status": "success",
                "data": cuenta,
                "message_for_user": f"Cuenta encontrada: '{cuenta.get('descripcion')}' (Código: {cuenta.get('codcuenta')})."
            }
        elif len(coincidencias) > 1:
            return {
                "status": "multiple",
                "data": coincidencias,
                "message_for_user": f"Se encontraron {len(coincidencias)} cuentas que coinciden con '{cuenta_input}'. Por favor, especifica el código exacto o ID si es posible."
            }
        else:
            return {
                "status": "not_found",
                "message": "No hay coincidencias",
                "message_for_user": f"No se encontró ninguna cuenta que contenga '{cuenta_input}' en su descripción o código."
            }

    except Exception as e:
        logger.error(f"Error al obtener cuenta '{cuenta_input}': {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al obtener la cuenta '{cuenta_input}': {str(e)}"
        }

# ----------- UPSERT -----------

def upsert_cuenta(tool_context, cuenta_id: Optional[str] = None, **kwargs: Any) -> dict:
    """
    Crea o actualiza una cuenta contable.
    Si se proporciona `cuenta_id`, actualiza. Si no, crea.
    
    Los únicos campos realmente obligatorios son:
    - codcuenta: Código de la cuenta (ej. 572000)
    - descripcion: Nombre descriptivo de la cuenta (ej. "Bancos")
    - codejercicio: Código del ejercicio contable al que pertenece
    
    El resto se rellenará con valores por defecto.
    """
    logger.info(f"TOOL EXECUTED: upsert_cuenta(cuenta_id='{cuenta_id}', kwargs={kwargs})")

    # Campos mínimos realmente necesarios
    required_fields = ["codcuenta", "descripcion", "codejercicio"]

    if not cuenta_id:
        # Validar solo los campos mínimos si es creación
        missing = [f for f in required_fields if f not in kwargs or kwargs[f] in [None, ""]]
        if missing:
            return {
                "status": "error",
                "message": f"Faltan campos obligatorios: {', '.join(missing)}",
                "message_for_user": f"Para crear una cuenta necesito como mínimo: {', '.join(missing)}"
            }
    
    # Obtener el ejercicio actual si no se proporciona
    if "codejercicio" not in kwargs:
        try:
            ejercicios_result = make_fs_request("GET", "/ejercicios")
            if ejercicios_result.get("status") == "success":
                ejercicios = ejercicios_result.get("data", [])
                # Buscar ejercicio actual (abierto)
                for ejercicio in ejercicios:
                    if ejercicio.get("estado") == "abierto":
                        kwargs["codejercicio"] = ejercicio.get("codejercicio")
                        break
                # Si no se encuentra, usar el primero de la lista
                if "codejercicio" not in kwargs and ejercicios:
                    kwargs["codejercicio"] = ejercicios[0].get("codejercicio")
        except Exception as e:
            logger.warning(f"Error al obtener ejercicio automático: {e}")
    
    # Valores por defecto para simplificar la creación
    defaults = {
        "codcuentaesp": "",         # Sin código especial por defecto
        "debe": 0.0,                # Saldo debe inicial cero
        "haber": 0.0,               # Saldo haber inicial cero
        "saldo": 0.0,               # Saldo total inicial cero
        "parent_codcuenta": "",     # Sin cuenta padre (cuenta raíz)
        "parent_idcuenta": ""       # Sin ID de cuenta padre (cuenta raíz)
    }
    
    # Aplicar defaults sólo para los campos que faltan
    for k, v in defaults.items():
        kwargs.setdefault(k, v)

    method = "PUT" if cuenta_id else "POST"
    endpoint = f"/cuentas/{cuenta_id}" if cuenta_id else "/cuentas"

    try:
        api_result = make_fs_request(method, endpoint, data=kwargs)
        if api_result.get("status") == "success":
            logger.info("Cuenta creada/actualizada correctamente")
            accion = "actualizada" if cuenta_id else "creada"
            descripcion = kwargs.get("descripcion", "sin descripción")
            codigo = kwargs.get("codcuenta", "")
            api_result.setdefault("message_for_user", 
                               f"Cuenta '{descripcion}' ({codigo}) {accion} correctamente.")
        else:
            logger.error(f"Error en upsert cuenta: {api_result}")
            api_result.setdefault("message_for_user", 
                               f"No pude guardar la cuenta. {api_result.get('message', '')}")
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