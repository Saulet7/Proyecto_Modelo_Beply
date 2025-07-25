import logging
from typing import Any, Optional
from utils import make_fs_request

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    filename="logs/contabilidad.log",  # ← aquí se define dónde se guardan
    filemode="a"
)
# ----------- LIST -----------

def list_impuestos(tool_context):
    """Lista todos los impuestos disponibles en el sistema."""
    logger.info("TOOL EXECUTED: list_impuestos()")
    try:
        api_result = make_fs_request("GET", "/impuestos")
        if api_result.get("status") == "success":
            logger.info("Listado de impuestos completado exitosamente")
            data = api_result.get("data", [])
            api_result.setdefault("message_for_user", f"Encontrados {len(data)} impuestos en el sistema.")
        else:
            logger.error(f"Error en listado de impuestos: {api_result}")
            api_result.setdefault("message_for_user", "No pude obtener la lista de impuestos.")
        return api_result
    except Exception as e:
        logger.error(f"Error al listar impuestos: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al obtener la lista de impuestos: {str(e)}"
        }

# ----------- GET -----------

def get_impuesto(tool_context, impuesto_input: str):
    """
    Obtiene información de uno o varios impuestos según ID, descripción o porcentaje IVA.

    Args:
        impuesto_input (str): ID del impuesto, descripción o porcentaje IVA a buscar.
    """
    logger.info(f"TOOL EXECUTED: get_impuesto(impuesto_input='{impuesto_input}')")
    try:
        api_result = make_fs_request("GET", f"/impuestos/{impuesto_input}")
        if api_result.get("status") == "success":
            logger.info("Impuesto obtenido correctamente")
            data = api_result.get("data", {})
            descripcion = data.get("descripcion", "Sin descripción")
            api_result.setdefault("message_for_user", f"Impuesto '{descripcion}' (ID: {impuesto_input}) obtenido correctamente.")
        else:
            logger.error(f"Error obteniendo impuesto: {api_result}")
            api_result.setdefault("message_for_user", f"No pude obtener el impuesto con ID {impuesto_input}.")
        return api_result
    except Exception as e:
        logger.error(f"Error al obtener impuesto {impuesto_input}: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al obtener el impuesto {impuesto_input}: {str(e)}"
        }

def upsert_impuesto(tool_context, impuesto_id: Optional[str] = None, **kwargs: Any) -> dict:
    """
    Crea o actualiza un impuesto.
    Si se proporciona `impuesto_id`, actualiza. Si no, crea.
    
    Los únicos campos realmente obligatorios son:
    - descripcion: Nombre descriptivo del impuesto (ej. "IVA General")
    - iva: Porcentaje del IVA (ej. 21.0)
    
    El resto se rellenará con valores por defecto.
    """
    logger.info(f"TOOL EXECUTED: upsert_impuesto(impuesto_id='{impuesto_id}', kwargs={kwargs})")

    # Campos mínimos realmente necesarios
    required_fields = ["descripcion", "iva"]

    if not impuesto_id:
        # Validar solo los campos mínimos si es creación
        # Verificar que los campos no estén vacíos ni sean None
        missing = []
        for field in required_fields:
            if field not in kwargs or kwargs[field] is None or kwargs[field] == "":
                missing.append(field)
        
        if missing:
            return {
                "status": "error",
                "message": f"Faltan campos obligatorios: {', '.join(missing)}",
                "message_for_user": f"Para crear un impuesto necesito como mínimo: {', '.join(missing)}"
            }
    
    # Valores por defecto para simplificar la creación
    defaults = {
        "activo": True,                # Activo por defecto
        "codimpuesto": "",             # Código autogenerado
        "codsubcuentarep": "477000",   # Subcuenta repercutido estándar
        "codsubcuentarepre": "477000", # Subcuenta repercutido RE estándar
        "codsubcuentasop": "472000",   # Subcuenta soportado estándar
        "codsubcuentasopre": "472000", # Subcuenta soportado RE estándar
        "recargo": 0.0,                # Sin recargo por defecto
        "tipo": 1                      # Tipo estándar
    }
    
    # Aplicar defaults sólo para los campos que faltan
    for k, v in defaults.items():
        kwargs.setdefault(k, v)

    method = "PUT" if impuesto_id else "POST"
    endpoint = f"/impuestos/{impuesto_id}" if impuesto_id else "/impuestos"

    try:
        # Asegurarse de que 'iva' sea un número
        if "iva" in kwargs and not isinstance(kwargs["iva"], (int, float)):
            try:
                kwargs["iva"] = float(kwargs["iva"])
            except (ValueError, TypeError):
                return {
                    "status": "error",
                    "message": "El valor de 'iva' debe ser un número",
                    "message_for_user": "El porcentaje de IVA debe ser un número válido"
                }

        api_result = make_fs_request(method, endpoint, data=kwargs)
        if api_result.get("status") == "success":
            logger.info("Impuesto creado/actualizado correctamente")
            accion = "actualizado" if impuesto_id else "creado"
            descripcion = kwargs.get("descripcion", "sin descripción")
            iva_info = f"IVA {kwargs.get('iva')}%"
            recargo_info = ""
            if kwargs.get("recargo") and kwargs.get("recargo") > 0:
                recargo_info = f" y recargo {kwargs.get('recargo')}%"
            
            api_result.setdefault("message_for_user", 
                               f"Impuesto '{descripcion}' ({iva_info}{recargo_info}) {accion} correctamente.")
        else:
            logger.error(f"Error en upsert impuesto: {api_result}")
            api_result.setdefault("message_for_user", 
                               f"No pude guardar el impuesto. {api_result.get('message', '')}")
        return api_result
    except Exception as e:
        logger.error(f"Error en upsert impuesto: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al guardar el impuesto: {str(e)}"
        }


# ----------- DELETE -----------

def delete_impuesto(tool_context, impuesto_id: str) -> dict:
    """
    Elimina un impuesto del sistema.
    """
    logger.info(f"TOOL EXECUTED: delete_impuesto(impuesto_id='{impuesto_id}')")

    if not impuesto_id:
        return {
            "status": "error",
            "message": "ID de impuesto obligatorio",
            "message_for_user": "Necesito el ID del impuesto para eliminarlo."
        }

    try:
        api_result = make_fs_request("DELETE", f"/impuestos/{impuesto_id}")
        if api_result.get("status") == "success":
            logger.info("Impuesto eliminado correctamente")
            api_result.setdefault("message_for_user", f"Impuesto con ID {impuesto_id} eliminado correctamente.")
        else:
            logger.error(f"Error eliminando impuesto: {api_result}")
            api_result.setdefault("message_for_user", f"No pude eliminar el impuesto {impuesto_id}.")
        return api_result
    except Exception as e:
        logger.error(f"Error eliminando impuesto {impuesto_id}: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al eliminar el impuesto {impuesto_id}: {str(e)}"
        }

# ----------- REGISTRO DE TOOLS -----------

IMPUESTOS_TOOLS = [
    list_impuestos,
    get_impuesto,
    upsert_impuesto,
    delete_impuesto
]
