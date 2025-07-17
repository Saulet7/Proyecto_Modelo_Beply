import logging
from typing import Optional, Any
from utils import make_fs_request

logger = logging.getLogger(__name__)

def list_lineafacturaclientes(tool_context):
    """
    Lista todas las líneas de factura de clientes disponibles en el sistema.
    """
    logger.info("TOOL EXECUTED: list_lineafacturaclientes()")
    
    try:
        # Usar make_fs_request para obtener la lista de líneas de factura
        api_result = make_fs_request("GET", "/lineafacturaclientes")
        
        if api_result.get("status") == "success":
            logger.info("Listado de líneas de factura completado exitosamente")
            lineas_data = api_result.get("data", [])
            if "message_for_user" not in api_result:
                api_result["message_for_user"] = f"Encontradas {len(lineas_data)} líneas de factura en el sistema."
            return api_result
        else:
            logger.error(f"Error en listado de líneas de factura: {api_result}")
            if "message_for_user" not in api_result:
                api_result["message_for_user"] = f"No pude obtener la lista de líneas de factura. Error: {api_result.get('message', 'desconocido')}."
            return api_result
        
    except Exception as e:
        logger.error(f"Error al listar líneas de factura: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al obtener la lista de líneas de factura: {str(e)}"
        }

def get_lineafacturacliente(tool_context, linea_id: str):
    """
    Obtiene información detallada de una línea de factura específica.
    
    Args:
        linea_id: ID de la línea de factura a consultar
    """
    logger.info(f"TOOL EXECUTED: get_lineafacturacliente(linea_id='{linea_id}')")
    
    try:
        # Usar make_fs_request para obtener la línea de factura específica
        api_result = make_fs_request("GET", f"/lineafacturaclientes/{linea_id}")
        
        if api_result.get("status") == "success":
            logger.info(f"Información de la línea de factura {linea_id} obtenida exitosamente")
            linea_data = api_result.get("data", {})
            if "message_for_user" not in api_result:
                descripcion = linea_data.get("descripcion", "Sin descripción") if linea_data else "Sin descripción"
                api_result["message_for_user"] = f"Información de la línea '{descripcion}' (ID: {linea_id}) obtenida correctamente."
            return api_result
        else:
            logger.error(f"Error obteniendo línea de factura {linea_id}: {api_result}")
            if "message_for_user" not in api_result:
                api_result["message_for_user"] = f"No pude encontrar la línea de factura con ID {linea_id}. Error: {api_result.get('message', 'desconocido')}."
            return api_result
        
    except Exception as e:
        logger.error(f"Error al obtener línea de factura {linea_id}: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Error al obtener información de la línea de factura {linea_id}: {str(e)}"
        }

def create_lineafacturacliente(tool_context, **kwargs: Any) -> dict:
    """
    Crea una nueva línea de factura de cliente.
    Envía datos como form-data.
    
    Args:
        **kwargs: Datos de la línea de factura (idfactura, cantidad, descripcion, etc.)
    """
    logger.info(f"TOOL EXECUTED: create_lineafacturacliente(kwargs={kwargs})")
    
    # Validar campos obligatorios básicos
    required_fields = ['idfactura', 'cantidad', 'descripcion']
    missing_fields = [field for field in required_fields if field not in kwargs or not kwargs[field]]
    
    if missing_fields:
        return {
            "status": "error",
            "message": f"Campos obligatorios faltantes: {', '.join(missing_fields)}",
            "message_for_user": f"Necesito los siguientes datos para crear la línea de factura: {', '.join(missing_fields)}"
        }
    
    # Preparar el diccionario de datos para enviar como formulario
    form_data = kwargs.copy()
    
    # Añadir valores por defecto para campos obligatorios de la API si no están presentes
    defaults = {
        'codimpuesto': 'GEN',
        'coste': kwargs.get('pvpunitario', 0) * 0.7 if 'pvpunitario' in kwargs else 0,
        'excepcioniva': '',
        'idlinearect': 0,
        'irpf': 0,
        'iva': 21,
        'recargo': 0,
        'linemeasurement': 1,
        'actualizastock': -1,
        'dtopor': 0,
        'dtopor2': 0,
        'mostrar_cantidad': True,
        'mostrar_precio': True,
        'orden': 0,
        'salto_pagina': False,
        'servido': 0,
        'suplido': False
    }
    
    # Añadir defaults solo si no están ya en form_data
    for key, value in defaults.items():
        if key not in form_data:
            form_data[key] = value
    
    # Calcular campos automáticos si no están presentes
    if 'pvpunitario' in form_data and 'cantidad' in form_data:
        if 'pvpsindto' not in form_data:
            form_data['pvpsindto'] = form_data['pvpunitario']
        if 'pvptotal' not in form_data:
            form_data['pvptotal'] = form_data['cantidad'] * form_data['pvpunitario']
    
    # MOSTRAR AL USUARIO QUÉ DATOS SE VAN A ENVIAR
    import json
    json_data = json.dumps(form_data, indent=2, ensure_ascii=False)
    logger.info(f"Datos que se enviarán a la API: {json_data}")
    
    # Llamar a make_fs_request, que enviará 'data' como form-data para POST
    api_result = make_fs_request("POST", "/lineafacturaclientes", data=form_data)
    
    # Añadir message_for_user a la respuesta
    if api_result.get("status") == "success" and "message_for_user" not in api_result:
        created_data = api_result.get("data", {})
        descripcion = created_data.get("descripcion", form_data.get("descripcion", "Sin descripción"))
        cantidad = created_data.get("cantidad", form_data.get("cantidad", 0))
        pvpunitario = created_data.get("pvpunitario", form_data.get("pvpunitario", 0))
        total = created_data.get("pvptotal", form_data.get("pvptotal", 0))
        api_result["message_for_user"] = f"Datos enviados a la API:\n{json_data}\n\n¡Línea de factura creada con éxito! {cantidad} x {descripcion} a {pvpunitario}€ cada una. Total: {total}€"
    elif api_result.get("status") == "error" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"Datos enviados a la API:\n{json_data}\n\nNo pude crear la línea de factura. Error: {api_result.get('message', 'desconocido')}."
    
    return api_result

def update_lineafacturacliente(tool_context, linea_id: str, **kwargs: Any) -> dict:
    """
    Actualiza la información de una línea de factura existente.
    Envía datos como form-data.
    
    Args:
        linea_id: ID de la línea de factura a actualizar
        **kwargs: Campos a actualizar (cantidad, descripcion, precio, etc.)
    """
    logger.info(f"TOOL EXECUTED: update_lineafacturacliente(linea_id='{linea_id}', kwargs={kwargs})")
    
    if not linea_id:
        return {
            "status": "error",
            "message": "ID de la línea de factura es obligatorio.",
            "message_for_user": "Necesito el ID de la línea de factura para poder actualizarla."
        }
    
    if not kwargs:
        return {
            "status": "error",
            "message": "No hay datos para actualizar.",
            "message_for_user": "No has proporcionado ningún dato para actualizar."
        }
    
    # Llamar a make_fs_request con los datos como form-data para PUT
    api_result = make_fs_request("PUT", f"/lineafacturaclientes/{linea_id}", data=kwargs)
    
    # Añadir message_for_user a la respuesta
    if api_result.get("status") == "success" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"Línea de factura con ID {linea_id} actualizada exitosamente."
    elif api_result.get("status") == "error" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"No pude actualizar la línea de factura con ID {linea_id}. Error: {api_result.get('message', 'desconocido')}."
    
    return api_result

def delete_lineafacturacliente(tool_context, linea_id: str) -> dict:
    """
    Elimina una línea de factura del sistema.
    
    Args:
        linea_id: ID de la línea de factura a eliminar
    """
    logger.info(f"TOOL EXECUTED: delete_lineafacturacliente(linea_id='{linea_id}')")
    
    if not linea_id:
        return {
            "status": "error",
            "message": "ID de la línea de factura es obligatorio.",
            "message_for_user": "Necesito el ID de la línea de factura para poder eliminarla."
        }
    
    # Llamar a make_fs_request para eliminar la línea de factura
    api_result = make_fs_request("DELETE", f"/lineafacturaclientes/{linea_id}")
    
    # Añadir message_for_user a la respuesta
    if api_result.get("status") == "success" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"Línea de factura con ID {linea_id} eliminada exitosamente."
    elif api_result.get("status") == "error" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"No pude eliminar la línea de factura con ID {linea_id}. Error: {api_result.get('message', 'desconocido')}."
    
    return api_result

# Lista de herramientas disponibles para el agente
LINEA_FACTURA_AGENT_TOOLS = [
    list_lineafacturaclientes,
    get_lineafacturacliente,
    create_lineafacturacliente,
    update_lineafacturacliente,
    delete_lineafacturacliente
]