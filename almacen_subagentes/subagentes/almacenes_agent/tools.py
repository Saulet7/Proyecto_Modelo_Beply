import logging
from typing import Optional, Any
from utils import make_fs_request

logger = logging.getLogger(__name__)

def list_warehouses(tool_context):
    logger.info("TOOL EXECUTED: list_warehouses()")
    try:
        api_result = make_fs_request("GET", "/almacenes")
        if api_result.get("status") == "success":
            data = api_result.get("data", [])
            api_result.setdefault("message_for_user", f"Se encontraron {len(data)} almacenes.")
        else:
            api_result.setdefault("message_for_user", "No se pudo obtener la lista de almacenes.")
        return api_result
    except Exception as e:
        logger.error(f"Error en list_warehouses: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al listar almacenes: {str(e)}"
        }

def create_warehouse(
    tool_context,
    codalmacen: str,
    nombre: str,
    direccion: str,
    ciudad: str,
    provincia: str,
    codpostal: str,
    codpais: str,
    telefono: str,
    idempresa: int,
    apartado: str
):
    logger.info(f"TOOL EXECUTED: create_warehouse(codalmacen='{codalmacen}')")

    # Validación de campos obligatorios
    required_fields = {
        "codalmacen": codalmacen,
        "nombre": nombre,
        "direccion": direccion,
        "ciudad": ciudad,
        "provincia": provincia,
        "codpostal": codpostal,
        "codpais": codpais,
        "telefono": telefono,
        "idempresa": idempresa,
        "apartado": apartado,
    }

    missing_fields = [field for field, value in required_fields.items() if value in [None, ""]]
    if missing_fields:
        return {
            "status": "error",
            "message": f"Faltan los siguientes campos requeridos: {', '.join(missing_fields)}",
            "message_for_user": "Debes completar todos los campos obligatorios del almacén."
        }

    try:
        response = make_fs_request("POST", "/almacenes", data=required_fields)
        if response.get("status") == "success":
            response.setdefault("message_for_user", f"Almacén '{codalmacen}' creado correctamente.")
        else:
            response.setdefault("message_for_user", f"No se pudo crear el almacén '{codalmacen}'.")
        return response
    except Exception as e:
        logger.error(f"Error al crear almacén: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al crear el almacén: {str(e)}"
        }

def update_warehouse(
    tool_context,
    id: str,
    codalmacen: Optional[str] = None,
    nombre: Optional[str] = None,
    direccion: Optional[str] = None,
    ciudad: Optional[str] = None,
    provincia: Optional[str] = None,
    codpostal: Optional[str] = None,
    codpais: Optional[str] = None,
    telefono: Optional[str] = None,
    idempresa: Optional[int] = None,
    apartado: Optional[str] = None
):
    logger.info(f"TOOL EXECUTED: update_warehouse(id='{id}')")

    if not id:
        return {
            "status": "error",
            "message": "El ID del almacén es obligatorio para actualizar.",
            "message_for_user": "No se puede actualizar un almacén sin identificarlo (ID requerido)."
        }

    # Construir el diccionario solo con campos que no sean None
    posibles_campos = {
        "codalmacen": codalmacen,
        "nombre": nombre,
        "direccion": direccion,
        "ciudad": ciudad,
        "provincia": provincia,
        "codpostal": codpostal,
        "codpais": codpais,
        "telefono": telefono,
        "idempresa": idempresa,
        "apartado": apartado,
    }

    form_data = {k: v for k, v in posibles_campos.items() if v is not None}

    if not form_data:
        return {
            "status": "error",
            "message": "No se especificó ningún campo a actualizar.",
            "message_for_user": "Debes indicar al menos un campo que quieras modificar del almacén."
        }

    try:
        response = make_fs_request("PUT", f"/almacenes/{id}", data=form_data)
        if response.get("status") == "success":
            response.setdefault("message_for_user", f"Almacén actualizado correctamente.")
        else:
            response.setdefault("message_for_user", f"No se pudo actualizar el almacén.")
        return response
    except Exception as e:
        logger.error(f"Error al actualizar almacén: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al actualizar el almacén: {str(e)}"
        }

def delete_warehouse(tool_context, warehouse_id: str):
    logger.info(f"TOOL EXECUTED: delete_warehouse(warehouse_id='{warehouse_id}')")
    if not warehouse_id:
        return {
            "status": "error",
            "message": "ID del almacén requerido.",
            "message_for_user": "Debes proporcionar el ID del almacén a eliminar."
        }
    try:
        api_result = make_fs_request("DELETE", f"/almacenes/{warehouse_id}")
        if api_result.get("status") == "success":
            api_result.setdefault("message_for_user", f"Almacén con ID '{warehouse_id}' eliminado correctamente.")
        else:
            api_result.setdefault("message_for_user", f"No se pudo eliminar el almacén con ID '{warehouse_id}'.")
        return api_result
    except Exception as e:
        logger.error(f"Error en delete_warehouse: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al eliminar el almacén: {str(e)}"
        }

AGENT_TOOLS = [
    list_warehouses,
    update_warehouse, 
    create_warehouse,
    delete_warehouse
]