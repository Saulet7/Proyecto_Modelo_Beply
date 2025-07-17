import logging
from typing import Optional, Any
from utils import make_fs_request


logger = logging.getLogger(__name__)

def list_facturaclientes(tool_context):
    """
    Lista todas las facturas de clientes disponibles en el sistema.
    """
    logger.info("TOOL EXECUTED: list_facturaclientes()")
    
    try:
        # Usar make_fs_request para obtener la lista de facturas
        api_result = make_fs_request("GET", "/facturaclientes")
        
        if api_result.get("status") == "success":
            logger.info("Listado de facturas completado exitosamente")
            facturas_data = api_result.get("data", [])
            if "message_for_user" not in api_result:
                api_result["message_for_user"] = f"Encontradas {len(facturas_data)} facturas en el sistema."
            return api_result
        else:
            logger.error(f"Error en listado de facturas: {api_result}")
            if "message_for_user" not in api_result:
                api_result["message_for_user"] = f"No pude obtener la lista de facturas. Error: {api_result.get('message', 'desconocido')}."
            return api_result
        
    except Exception as e:
        logger.error(f"Error al listar facturas: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al obtener la lista de facturas: {str(e)}"
        }

def get_facturacliente(tool_context, factura_id: str):
    """
    Obtiene información detallada de una factura específica.
    
    Args:
        factura_id: ID de la factura a consultar
    """
    logger.info(f"TOOL EXECUTED: get_facturacliente(factura_id='{factura_id}')")
    
    try:
        # Usar make_fs_request para obtener la factura específica
        api_result = make_fs_request("GET", f"/facturaclientes/{factura_id}")
        
        if api_result.get("status") == "success":
            logger.info(f"Información de la factura {factura_id} obtenida exitosamente")
            factura_data = api_result.get("data", {})
            if "message_for_user" not in api_result:
                numero = factura_data.get("numero", "Sin número") if factura_data else "Sin número"
                api_result["message_for_user"] = f"Información de la factura '{numero}' (ID: {factura_id}) obtenida correctamente."
            return api_result
        else:
            logger.error(f"Error obteniendo factura {factura_id}: {api_result}")
            if "message_for_user" not in api_result:
                api_result["message_for_user"] = f"No pude encontrar la factura con ID {factura_id}. Error: {api_result.get('message', 'desconocido')}."
            return api_result
        
    except Exception as e:
        logger.error(f"Error al obtener factura {factura_id}: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al obtener información de la factura {factura_id}: {str(e)}"
        }

def create_facturacliente(tool_context, codcliente: str, **kwargs: Any) -> dict:
    """
    Crea una nueva factura de cliente. codcliente es obligatorio.
    Envía datos como form-data.
    
    Args:
        codcliente: Código del cliente (obligatorio)
        **kwargs: Otros datos de la factura (fecha, numero, total, etc.)
    """
    logger.info(f"TOOL EXECUTED: create_facturacliente(codcliente='{codcliente}', kwargs={kwargs})")
    
    if not codcliente:
        return {
            "status": "error",
            "message": "Código de cliente es obligatorio.",
            "message_for_user": "Necesito el código del cliente para crear una nueva factura."
        }
    
    # Preparar el diccionario de datos para enviar como formulario
    form_data = {'codcliente': codcliente}
    form_data.update(kwargs)
    
    # MOSTRAR AL USUARIO QUÉ DATOS SE VAN A ENVIAR
    import json
    json_data = json.dumps(form_data, indent=2, ensure_ascii=False)
    logger.info(f"Datos que se enviarán a la API: {json_data}")
    
    # Llamar a make_fs_request, que enviará 'data' como form-data para POST
    api_result = make_fs_request("POST", "/facturaclientes", data=form_data)
    
    # Añadir message_for_user a la respuesta
    if api_result.get("status") == "success" and "message_for_user" not in api_result:
        created_data = api_result.get("data", {})
        numero = created_data.get("numero", "Sin número") if created_data else "Sin número"
        api_result["message_for_user"] = f"Datos enviados a la API:\n{json_data}\n\n¡Factura creada con éxito! Número: {numero} (Cliente: {codcliente})"
    elif api_result.get("status") == "error" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"Datos enviados a la API:\n{json_data}\n\nNo pude crear la factura para el cliente '{codcliente}'. Error: {api_result.get('message', 'desconocido')}."
    
    return api_result

def update_facturacliente(tool_context, factura_id: str, **kwargs: Any) -> dict:
    """
    Actualiza la información de una factura existente.
    Envía datos como form-data.
    
    Args:
        factura_id: ID de la factura a actualizar
        **kwargs: Campos a actualizar (codcliente, fecha, total, etc.)
    """
    logger.info(f"TOOL EXECUTED: update_facturacliente(factura_id='{factura_id}', kwargs={kwargs})")
    
    if not factura_id:
        return {
            "status": "error",
            "message": "ID de la factura es obligatorio.",
            "message_for_user": "Necesito el ID de la factura para poder actualizarla."
        }
    
    if not kwargs:
        return {
            "status": "error",
            "message": "No hay datos para actualizar.",
            "message_for_user": "No has proporcionado ningún dato para actualizar."
        }
    
    # Llamar a make_fs_request con los datos como form-data para PUT
    api_result = make_fs_request("PUT", f"/facturaclientes/{factura_id}", data=kwargs)
    
    # Añadir message_for_user a la respuesta
    if api_result.get("status") == "success" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"Factura con ID {factura_id} actualizada exitosamente."
    elif api_result.get("status") == "error" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"No pude actualizar la factura con ID {factura_id}. Error: {api_result.get('message', 'desconocido')}."
    
    return api_result

def delete_facturacliente(tool_context, factura_id: str) -> dict:
    """
    Elimina una factura del sistema.
    
    Args:
        factura_id: ID de la factura a eliminar
    """
    logger.info(f"TOOL EXECUTED: delete_facturacliente(factura_id='{factura_id}')")
    
    if not factura_id:
        return {
            "status": "error",
            "message": "ID de la factura es obligatorio.",
            "message_for_user": "Necesito el ID de la factura para poder eliminarla."
        }
    
    # Llamar a make_fs_request para eliminar la factura
    api_result = make_fs_request("DELETE", f"/facturaclientes/{factura_id}")
    
    # Añadir message_for_user a la respuesta
    if api_result.get("status") == "success" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"Factura con ID {factura_id} eliminada exitosamente."
    elif api_result.get("status") == "error" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"No pude eliminar la factura con ID {factura_id}. Error: {api_result.get('message', 'desconocido')}."
    
    return api_result

def get_factura(tool_context, factura_input: str):
    """
    Obtiene información de una o varias facturas según ID o código de cliente.
    """
    logger.info(f"TOOL EXECUTED: get_factura(factura_input='{factura_input}')")

    def es_numero(valor: str) -> bool:
        return valor.isdigit()

    try:
        # Primero intentar buscar por código de cliente (listado + filtro)
        all_result = make_fs_request("GET", "/facturaclientes")
        if all_result.get("status") == "success":
            facturas = all_result.get("data", [])
            
            # Buscar por código de cliente
            coincidencias = [
                {
                    "idfactura": f.get("idfactura"),
                    "numero": f.get("numero"),
                    "codcliente": f.get("codcliente"),
                    "fecha": f.get("fecha"),
                    "total": f.get("total"),
                    "status": "found"
                }
                for f in facturas
                if str(factura_input) == str(f.get("codcliente"))
            ]
            
            if coincidencias:
                if len(coincidencias) == 1:
                    factura = coincidencias[0]
                    return {
                        "status": "success",
                        "data": factura,
                        "message_for_user": f"Factura encontrada: '{factura['numero']}' (ID: {factura['idfactura']}) - Cliente: {factura['codcliente']}."
                    }
                else:
                    return {
                        "status": "multiple",
                        "data": coincidencias,
                        "message_for_user": f"Se encontraron {len(coincidencias)} facturas para el cliente '{factura_input}'.",
                    }
        
        # Si no se encontró por codcliente y es numérico, buscar por ID de factura
        if es_numero(factura_input):
            api_result = make_fs_request("GET", f"/facturaclientes/{factura_input}")
            if api_result.get("status") == "success":
                factura_data = api_result.get("data", {})
                if factura_data:
                    return {
                        "status": "success",
                        "data": {
                            "idfactura": factura_data.get("idfactura"),
                            "numero": factura_data.get("numero"),
                            "codcliente": factura_data.get("codcliente"),
                            "fecha": factura_data.get("fecha"),
                            "total": factura_data.get("total"),
                            "status": "found"
                        },
                        "message_for_user": f"Factura encontrada: '{factura_data.get('numero')}' (ID: {factura_data.get('idfactura')}) - Cliente: {factura_data.get('codcliente')}."
                    }
        
        # No se encontró nada
        return {
            "status": "not_found",
            "message": "No hay coincidencias",
            "message_for_user": f"No se encontró ninguna factura para el cliente '{factura_input}'."
        }

    except Exception as e:
        logger.error(f"Error al obtener factura '{factura_input}': {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al obtener la factura '{factura_input}': {str(e)}"
        }

# Lista de herramientas disponibles para el agente
FACTURA_AGENT_TOOLS = [
    list_facturaclientes,
    get_facturacliente,
    create_facturacliente,
    update_facturacliente,
    delete_facturacliente,
    get_factura
]
