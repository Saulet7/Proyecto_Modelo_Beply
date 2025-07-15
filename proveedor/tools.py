import logging
from typing import Optional, Any
from utils import make_fs_request

logger = logging.getLogger(__name__)

def list_proveedores(tool_context):
    logger.info("TOOL EXECUTED: list_proveedores()")
    try:
        api_result = make_fs_request("GET", "/proveedores")
        if api_result.get("status") == "success":
            proveedores_data = api_result.get("data", [])
            if "message_for_user" not in api_result:
                api_result["message_for_user"] = f"Encontrados {len(proveedores_data)} proveedores en el sistema."
            return api_result
        else:
            logger.error(f"Error en listado de proveedores: {api_result}")
            if "message_for_user" not in api_result:
                api_result["message_for_user"] = f"No pude obtener la lista de proveedores. Error: {api_result.get('message', 'desconocido')}."
            return api_result
    except Exception as e:
        logger.error(f"Error al listar proveedores: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al obtener la lista de proveedores: {str(e)}"
        }

def get_proveedor(tool_context, proveedor_id: str):
    logger.info(f"TOOL EXECUTED: get_proveedor(proveedor_id='{proveedor_id}')")
    try:
        api_result = make_fs_request("GET", f"/proveedores/{proveedor_id}")
        if api_result.get("status") == "success":
            proveedor_data = api_result.get("data", {})
            if "message_for_user" not in api_result:
                nombre = proveedor_data.get("nombre", "Sin nombre")
                api_result["message_for_user"] = f"Información del proveedor '{nombre}' (ID: {proveedor_id}) obtenida correctamente."
            return api_result
        else:
            logger.error(f"Error obteniendo proveedor {proveedor_id}: {api_result}")
            if "message_for_user" not in api_result:
                api_result["message_for_user"] = f"No pude encontrar el proveedor con ID {proveedor_id}. Error: {api_result.get('message', 'desconocido')}."
            return api_result
    except Exception as e:
        logger.error(f"Error al obtener proveedor {proveedor_id}: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al obtener información del proveedor {proveedor_id}: {str(e)}"
        }

def create_proveedor(tool_context, nombre: str, cifnif: str, email: Optional[str] = None, telefono1: Optional[str] = None, **kwargs: Any):
    logger.info(f"TOOL EXECUTED: create_proveedor(nombre='{nombre}', cifnif='{cifnif}', email='{email}', telefono1='{telefono1}', kwargs={kwargs})")
    
    if not nombre or not cifnif:
        return {
            "status": "error",
            "message": "Nombre y CIF/NIF obligatorios.",
            "message_for_user": "Necesito tanto el nombre como el NIF/CIF para crear un nuevo proveedor."
        }
    
    form_data = {'nombre': nombre, 'cifnif': cifnif}
    if email: form_data['email'] = email
    if telefono1: form_data['telefono1'] = telefono1
    form_data.update(kwargs)

    api_result = make_fs_request("POST", "/proveedores", data=form_data)

    if api_result.get("status") == "success" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"¡Proveedor '{nombre}' creado con éxito! (NIF/CIF: {cifnif})"
    elif api_result.get("status") == "error" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"No pude crear el proveedor '{nombre}'. Error: {api_result.get('message', 'desconocido')}."
    
    return api_result

def update_proveedor(tool_context, proveedor_id: str, **kwargs: Any):
    logger.info(f"TOOL EXECUTED: update_proveedor(proveedor_id='{proveedor_id}', kwargs={kwargs})")
    
    if not proveedor_id:
        return {
            "status": "error",
            "message": "ID del proveedor es obligatorio.",
            "message_for_user": "Necesito el ID del proveedor para poder actualizarlo."
        }

    if not kwargs:
        return {
            "status": "error",
            "message": "No hay datos para actualizar.",
            "message_for_user": "No has proporcionado ningún dato para actualizar."
        }

    api_result = make_fs_request("PUT", f"/proveedores/{proveedor_id}", data=kwargs)

    if api_result.get("status") == "success" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"Proveedor con ID {proveedor_id} actualizado exitosamente."
    elif api_result.get("status") == "error" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"No pude actualizar el proveedor con ID {proveedor_id}. Error: {api_result.get('message', 'desconocido')}."
    
    return api_result

def delete_proveedor(tool_context, proveedor_id: str):
    logger.info(f"TOOL EXECUTED: delete_proveedor(proveedor_id='{proveedor_id}')")
    
    if not proveedor_id:
        return {
            "status": "error",
            "message": "ID del proveedor es obligatorio.",
            "message_for_user": "Necesito el ID del proveedor para poder eliminarlo."
        }

    api_result = make_fs_request("DELETE", f"/proveedores/{proveedor_id}")

    if api_result.get("status") == "success" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"Proveedor con ID {proveedor_id} eliminado exitosamente."
    elif api_result.get("status") == "error" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"No pude eliminar el proveedor con ID {proveedor_id}. Error: {api_result.get('message', 'desconocido')}."
    
    return api_result

# Lista de herramientas para el agente de proveedores
PROVEEDOR_AGENT_TOOLS = [
    list_proveedores,
    get_proveedor,
    create_proveedor,
    update_proveedor,
    delete_proveedor
]
