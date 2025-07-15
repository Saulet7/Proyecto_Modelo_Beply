import logging
import json
from typing import Optional, Any
from utils import make_fs_request
import re

logger = logging.getLogger(__name__)

def list_clientes(tool_context):
    """
    Lista todos los clientes disponibles en el sistema.
    """
    logger.info("TOOL EXECUTED: list_clientes()")
    
    try:
        # Usar make_fs_request para obtener la lista de clientes
        api_result = make_fs_request("GET", "/clientes")
        
        if api_result.get("status") == "success":
            logger.info("Listado de clientes completado exitosamente")
            clientes_data = api_result.get("data", [])
            if "message_for_user" not in api_result:
                api_result["message_for_user"] = f"Encontrados {len(clientes_data)} clientes en el sistema."
            return api_result
        else:
            logger.error(f"Error en listado de clientes: {api_result}")
            if "message_for_user" not in api_result:
                api_result["message_for_user"] = f"No pude obtener la lista de clientes. Error: {api_result.get('message', 'desconocido')}."
            return api_result
        
    except Exception as e:
        logger.error(f"Error al listar clientes: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al obtener la lista de clientes: {str(e)}"
        }

def get_cliente(tool_context, cliente_input: str):
    """
    Obtiene información de uno o varios clientes según ID, nombre exacto o parcial.

    Args:
        cliente_input (str): ID del cliente o parte del nombre a buscar.
    """
    logger.info(f"TOOL EXECUTED: get_cliente(cliente_input='{cliente_input}')")

    def es_uuid(valor: str) -> bool:
        return re.fullmatch(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}", valor
        ) is not None

    try:
        if es_uuid(cliente_input):
            # Buscar directamente por ID
            api_result = make_fs_request("GET", f"/clientes/{cliente_input}")
            if api_result.get("status") == "success":
                cliente_data = api_result.get("data", {})
                if cliente_data:
                    return {
                        "status": "success",
                        "data": {
                            "codcliente": cliente_data.get("codcliente"),
                            "nombre": cliente_data.get("nombre"),
                            "cifnif": cliente_data.get("cifnif"),
                            "status": "found"
                        },
                        "message_for_user": f"Cliente encontrado: '{cliente_data.get('nombre')}' (ID: {cliente_data.get('codcliente')})."
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Cliente no encontrado",
                        "message_for_user": f"No se encontró un cliente con ID '{cliente_input}'."
                    }

        # Buscar por nombre parcial (listado + filtro)
        all_result = make_fs_request("GET", "/clientes")
        if all_result.get("status") != "success":
            return {
                "status": "error",
                "message": "Error al obtener lista de clientes",
                "message_for_user": "No pude obtener la lista de clientes para buscar coincidencias."
            }

        clientes = all_result.get("data", [])
        coincidencias = [
            {
                "codcliente": c.get("codcliente"),
                "nombre": c.get("nombre"),
                "cifnif": c.get("cifnif"),
                "status": "found"
            }
            for c in clientes
            if cliente_input.lower() in (c.get("nombre") or "").lower()
        ]

        if len(coincidencias) == 1:
            cliente = coincidencias[0]
            return {
                "status": "success",
                "data": cliente,
                "message_for_user": f"Cliente encontrado: '{cliente['nombre']}' (ID: {cliente['codcliente']})."
            }
        elif len(coincidencias) > 1:
            return {
                "status": "multiple",
                "data": coincidencias,
                "message_for_user": f"Se encontraron {len(coincidencias)} clientes que coinciden con '{cliente_input}'. Por favor, especifica el NIF/CIF o ID si es posible."
            }
        else:
            return {
                "status": "not_found",
                "message": "No hay coincidencias",
                "message_for_user": f"No se encontró ningún cliente que contenga '{cliente_input}' en su nombre."
            }

    except Exception as e:
        logger.error(f"Error al obtener cliente '{cliente_input}': {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al obtener el cliente '{cliente_input}': {str(e)}"
        }



def create_cliente(tool_context, nombre: str, cifnif: str, email: Optional[str] = None, telefono1: Optional[str] = None, **kwargs: Any) -> dict:
    """
    Crea un nuevo cliente. Nombre y CIF/NIF son obligatorios.
    Envía datos como form-data.
    
    Args:
        nombre: Nombre del cliente (obligatorio)
        cifnif: CIF/NIF del cliente (obligatorio)
        email: Email del cliente (opcional)
        telefono1: Teléfono del cliente (opcional)
        **kwargs: Otros datos del cliente
    """
    logger.info(f"TOOL EXECUTED: create_cliente(nombre='{nombre}', cifnif='{cifnif}', email='{email}', telefono1='{telefono1}', kwargs={kwargs})")
    
    if not nombre or not cifnif: 
        return {
            "status": "error", 
            "message": "Nombre y CIF/NIF obligatorios.", 
            "message_for_user": "Necesito tanto el nombre como el NIF/CIF para crear un nuevo cliente."
        }
    
    # Preparar el diccionario de datos para enviar como formulario
    form_data = {'nombre': nombre, 'cifnif': cifnif}
    if email: form_data['email'] = email
    if telefono1: form_data['telefono1'] = telefono1
    form_data.update(kwargs)
    
    # Llamar a make_fs_request, que enviará 'data' como form-data para POST
    api_result = make_fs_request("POST", "/clientes", data=form_data)
    
    # Añadir message_for_user a la respuesta
    if api_result.get("status") == "success" and "message_for_user" not in api_result:
        created_data = api_result.get("data", {})
        codcliente = created_data.get("codcliente", "") if created_data else ""
        api_result["message_for_user"] = f"¡Cliente '{nombre}' creado con éxito! (NIF/CIF: {cifnif})"
    elif api_result.get("status") == "error" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"No pude crear el cliente '{nombre}'. Error: {api_result.get('message', 'desconocido')}."
    
    return api_result

def update_cliente(tool_context, cliente_id: str, **kwargs: Any) -> dict:
    """
    Actualiza la información de un cliente existente.
    Envía datos como form-data.
    
    Args:
        cliente_id: ID del cliente a actualizar
        **kwargs: Campos a actualizar (nombre, cifnif, email, telefono1, etc.)
    """
    logger.info(f"TOOL EXECUTED: update_cliente(cliente_id='{cliente_id}', kwargs={kwargs})")
    
    if not cliente_id:
        return {
            "status": "error",
            "message": "ID del cliente es obligatorio.",
            "message_for_user": "Necesito el ID del cliente para poder actualizarlo."
        }
    
    if not kwargs:
        return {
            "status": "error",
            "message": "No hay datos para actualizar.",
            "message_for_user": "No has proporcionado ningún dato para actualizar."
        }
    
    # Llamar a make_fs_request con los datos como form-data para PUT
    api_result = make_fs_request("PUT", f"/clientes/{cliente_id}", data=kwargs)
    
    # Añadir message_for_user a la respuesta
    if api_result.get("status") == "success" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"Cliente con ID {cliente_id} actualizado exitosamente."
    elif api_result.get("status") == "error" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"No pude actualizar el cliente con ID {cliente_id}. Error: {api_result.get('message', 'desconocido')}."
    
    return api_result

def delete_cliente(tool_context, cliente_id: str) -> dict:
    """
    Elimina un cliente del sistema.
    
    Args:
        cliente_id: ID del cliente a eliminar
    """
    logger.info(f"TOOL EXECUTED: delete_cliente(cliente_id='{cliente_id}')")
    
    if not cliente_id:
        return {
            "status": "error",
            "message": "ID del cliente es obligatorio.",
            "message_for_user": "Necesito el ID del cliente para poder eliminarlo."
        }
    
    # Llamar a make_fs_request para eliminar el cliente
    api_result = make_fs_request("DELETE", f"/clientes/{cliente_id}")
    
    # Añadir message_for_user a la respuesta
    if api_result.get("status") == "success" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"Cliente con ID {cliente_id} eliminado exitosamente."
    elif api_result.get("status") == "error" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"No pude eliminar el cliente con ID {cliente_id}. Error: {api_result.get('message', 'desconocido')}."
    
    return api_result

# Función de diagnóstico para testing
def test_api_connection(tool_context) -> dict:
    """
    Prueba la conectividad con la API de BEPLY.
    """
    logger.info("TOOL EXECUTED: test_api_connection()")
    
    try:
        # Probar conexión con GET /clientes
        api_result = make_fs_request("GET", "/clientes")
        
        if api_result.get("status") == "success":
            clientes_data = api_result.get("data", [])
            return {
                "status": "success",
                "message": "Conectividad API exitosa",
                "message_for_user": f"✅ Conexión API exitosa. Se encontraron {len(clientes_data)} clientes."
            }
        else:
            return {
                "status": "error",
                "message": f"Error de conectividad: {api_result.get('message', 'desconocido')}",
                "message_for_user": f"❌ Error de conexión con la API: {api_result.get('message', 'desconocido')}"
            }
            
    except Exception as e:
        logger.error(f"Error al probar conexión API: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"❌ Error al probar la conexión: {str(e)}"
        }

# Lista de herramientas disponibles para el agente
CLIENTE_AGENT_TOOLS = [
    list_clientes,
    get_cliente,
    create_cliente,
    update_cliente,
    delete_cliente,
    test_api_connection
]

# Configuración de logging para debugging
def setup_debug_logging():
    """Configura el logging detallado para debugging"""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # Handler para archivo
    file_handler = logging.FileHandler('cliente_api_debug.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Añadir handlers
    logger.handlers.clear()  # Limpiar handlers existentes
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info("Logging de debugging configurado")

# Llamar setup al importar el módulo
setup_debug_logging()
