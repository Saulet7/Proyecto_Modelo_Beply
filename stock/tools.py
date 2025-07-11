import logging
from typing import Any
from utils import make_fs_request

logger = logging.getLogger(__name__)

def list_stock(tool_context):
    """
    Lista todos los registros de stock disponibles en el sistema.
    """
    logger.info("TOOL EXECUTED: list_stock()")
    api_result = make_fs_request("GET", "/stocks")  # Corregido: /stocks (plural)
    if "message_for_user" not in api_result:
        api_result["message_for_user"] = f"Encontrados {len(api_result.get('data', []))} registros de stock."
    return api_result

def get_stock(tool_context, stock_id: str) -> dict:
    """
    Obtiene detalles completos de un registro de stock específico.
    
    Args:
        stock_id: ID del registro de stock a consultar
    """
    logger.info(f"TOOL EXECUTED: get_stock(stock_id='{stock_id}')")
    api_result = make_fs_request("GET", f"/stocks/{stock_id}")  # Corregido: /stocks (plural)
    if api_result.get("status") == "success" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"Información del stock {stock_id} obtenida correctamente."
    elif api_result.get("status") == "error" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"No pude encontrar el stock con ID {stock_id}. Error: {api_result.get('message', 'desconocido')}."
    return api_result

def create_stock(tool_context, **kwargs: Any) -> dict:
    """
    Crea un nuevo registro de stock en el sistema.
    
    Args:
        **kwargs: Datos del registro de stock (cantidad, codalmacen, etc.)
    """
    logger.info(f"TOOL EXECUTED: create_stock(kwargs={kwargs})")
    # Campos requeridos y valores por defecto
    required_fields = {
        "cantidad": 1,
        "codalmacen": "",
        "disponible": 0,
        "idproducto": 0,
        "pterecibir": 0,
        "referencia": "",
        "reservada": 0,
        "stockmax": 0,
        "stockmin": 0,
        "ubicacion": ""
    }
    # Eliminar idstock de los valores por defecto ya que la API lo generará
    form_data = {k: kwargs.get(k, v) for k, v in required_fields.items()}
    
    import json
    json_data = json.dumps(form_data, indent=2, ensure_ascii=False)
    logger.info(f"Datos que se enviarán a la API: {json_data}")
    
    api_result = make_fs_request("POST", "/stocks", data=form_data)  # Corregido: /stocks (plural)
    
    if api_result.get("status") == "success" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"Datos enviados a la API:\n{json_data}\n\n¡Stock creado con éxito!"
    elif api_result.get("status") == "error" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"Datos enviados a la API:\n{json_data}\n\nNo pude crear el stock. Error: {api_result.get('message', 'desconocido')}."
    
    return api_result

def update_stock(tool_context, stock_id: str, **kwargs: Any) -> dict:
    """
    Actualiza un registro de stock existente.
    
    Args:
        stock_id: ID del registro de stock a actualizar
        **kwargs: Datos a actualizar (cantidad, codalmacen, etc.)
    """
    logger.info(f"TOOL EXECUTED: update_stock(stock_id='{stock_id}', kwargs={kwargs})")
    
    import json
    json_data = json.dumps(kwargs, indent=2, ensure_ascii=False)
    logger.info(f"Datos que se enviarán a la API: {json_data}")
    
    api_result = make_fs_request("PUT", f"/stocks/{stock_id}", data=kwargs)  # Corregido: /stocks (plural)
    
    if api_result.get("status") == "success" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"Datos enviados a la API:\n{json_data}\n\nStock con ID {stock_id} actualizado exitosamente."
    elif api_result.get("status") == "error" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"Datos enviados a la API:\n{json_data}\n\nNo pude actualizar el stock con ID {stock_id}. Error: {api_result.get('message', 'desconocido')}."
    
    return api_result

def delete_stock(tool_context, stock_id: str) -> dict:
    """
    Elimina un registro de stock del sistema.
    
    Args:
        stock_id: ID del registro de stock a eliminar
    """
    logger.info(f"TOOL EXECUTED: delete_stock(stock_id='{stock_id}')")
    
    api_result = make_fs_request("DELETE", f"/stocks/{stock_id}")  # Corregido: /stocks (plural)
    
    if api_result.get("status") == "success" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"Stock con ID {stock_id} eliminado exitosamente."
    elif api_result.get("status") == "error" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"No pude eliminar el stock con ID {stock_id}. Error: {api_result.get('message', 'desconocido')}."
    
    return api_result

# Lista de herramientas disponibles para el agente
STOCK_AGENT_TOOLS = [
    list_stock,
    get_stock,
    create_stock,
    update_stock,
    delete_stock
]