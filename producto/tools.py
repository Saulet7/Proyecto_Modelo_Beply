import logging
import json
from typing import Any
from utils import make_fs_request

logger = logging.getLogger(__name__)

def list_productos(tool_context):
    """
    Lista todos los productos disponibles en el sistema.
    """
    logger.info("TOOL EXECUTED: list_productos()")
    api_result = make_fs_request("GET", "/productos")
    if "message_for_user" not in api_result:
        api_result["message_for_user"] = f"Encontrados {len(api_result.get('data', []))} productos."
    return api_result

def get_producto(tool_context, producto_id: str) -> dict:
    """
    Obtiene detalles completos de un producto específico.
    
    Args:
        producto_id: ID del producto a consultar
    """
    logger.info(f"TOOL EXECUTED: get_producto(producto_id='{producto_id}')")
    api_result = make_fs_request("GET", f"/productos/{producto_id}")
    if api_result.get("status") == "success" and "message_for_user" not in api_result:
        producto_data = api_result.get("data", {})
        descripcion = producto_data.get("descripcion", "Sin descripción")
        referencia = producto_data.get("referencia", "Sin referencia")
        api_result["message_for_user"] = f"Información del producto '{descripcion}' (Ref: {referencia}) obtenida correctamente."
    elif api_result.get("status") == "error" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"No pude encontrar el producto con ID {producto_id}. Error: {api_result.get('message', 'desconocido')}."
    return api_result

def create_producto(tool_context, **kwargs: Any) -> dict:
    """
    Crea un nuevo producto en el sistema.
    
    Args:
        **kwargs: Datos del producto (referencia, descripción, precio, etc.)
    """
    logger.info(f"TOOL EXECUTED: create_producto(kwargs={kwargs})")
    
    # COMPROBACIÓN DE SEGURIDAD: Si no hay referencia o descripción, forzar salida
    if not kwargs.get("referencia") or not kwargs.get("descripcion"):
        mensaje = "Necesito más información para crear el producto. Por favor, proporciona:"
        if not kwargs.get("referencia"):
            mensaje += "\n- Referencia del producto (código único)"
        if not kwargs.get("descripcion"):
            mensaje += "\n- Descripción completa del producto"
        
        # Forzar salida del bucle
        return {
            "status": "need_more_info",
            "message_for_user": mensaje,
            "force_exit": True
        }
    
    # Si llegamos aquí, tenemos los datos necesarios
    # Fecha actual para valores por defecto
    from datetime import datetime
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Campos con valores por defecto
    required_fields = {
        # Datos proporcionados por el usuario
        "referencia": kwargs.get("referencia"),
        "descripcion": kwargs.get("descripcion"),
        "precio": kwargs.get("precio", 0),
        
        # Valores por defecto
        "codfamilia": kwargs.get("codfamilia", "GEN"),        
        "codfabricante": kwargs.get("codfabricante", "GEN"),  
        "codimpuesto": kwargs.get("codimpuesto", "IVA21"),    
        "fechaalta": kwargs.get("fechaalta", fecha_actual),
        "tipo": kwargs.get("tipo", "producto"),               
        "excepcioniva": kwargs.get("excepcioniva", "0"),      
        "codsubcuentacom": kwargs.get("codsubcuentacom", "COMPRAS"),
        "codsubcuentaven": kwargs.get("codsubcuentaven", "VENTAS"),
        "codsubcuentairpfcom": kwargs.get("codsubcuentairpfcom", "IRPFCOM"),
        "observaciones": kwargs.get("observaciones", ""),
        "actualizado": kwargs.get("actualizado", fecha_hora_actual),
        "stockfis": kwargs.get("stockfis", 0),
        # Convertir booleanos a enteros (0/1) para la API
        "bloqueado": 1 if kwargs.get("bloqueado") else 0,
        "secompra": 1 if kwargs.get("secompra", True) else 0,
        "sevende": 1 if kwargs.get("sevende", True) else 0,
        "nostock": 1 if kwargs.get("nostock") else 0,
        "publico": 1 if kwargs.get("publico") else 0,
        "ventasinstock": 1 if kwargs.get("ventasinstock") else 0,
        "measurement": kwargs.get("measurement", 0)
    }
    
    # Mostrar datos a enviar
    json_data = json.dumps(required_fields, indent=2, ensure_ascii=False)
    logger.info(f"Datos que se enviarán a la API: {json_data}")
    
    # Llamar a la API
    api_result = make_fs_request("POST", "/productos", data=required_fields)
    
    # Procesar respuesta
    if api_result.get("status") == "success" and "message_for_user" not in api_result:
        created_data = api_result.get("data", {})
        descripcion = created_data.get("descripcion", "Sin descripción")
        referencia = created_data.get("referencia", "Sin referencia")
        api_result["message_for_user"] = f"¡Producto '{descripcion}' (Ref: {referencia}) creado con éxito!"
    elif api_result.get("status") == "error" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"No pude crear el producto. Error: {api_result.get('message', 'desconocido')}."
    
    return api_result

def update_producto(tool_context, producto_id: str, **kwargs: Any) -> dict:
    """
    Actualiza un producto existente.
    
    Args:
        producto_id: ID del producto a actualizar
        **kwargs: Datos a actualizar
    """
    logger.info(f"TOOL EXECUTED: update_producto(producto_id='{producto_id}', kwargs={kwargs})")
    
    # Mostrar datos a enviar
    json_data = json.dumps(kwargs, indent=2, ensure_ascii=False)
    logger.info(f"Datos que se enviarán a la API: {json_data}")
    
    # Llamar a la API
    api_result = make_fs_request("PUT", f"/productos/{producto_id}", data=kwargs)
    
    # Procesar respuesta
    if api_result.get("status") == "success" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"Datos enviados a la API:\n{json_data}\n\nProducto con ID {producto_id} actualizado exitosamente."
    elif api_result.get("status") == "error" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"Datos enviados a la API:\n{json_data}\n\nNo pude actualizar el producto con ID {producto_id}. Error: {api_result.get('message', 'desconocido')}."
    
    return api_result

def delete_producto(tool_context, producto_id: str) -> dict:
    """
    Elimina un producto del sistema.
    
    Args:
        producto_id: ID del producto a eliminar
    """
    logger.info(f"TOOL EXECUTED: delete_producto(producto_id='{producto_id}')")
    
    # Llamar a la API
    api_result = make_fs_request("DELETE", f"/productos/{producto_id}")
    
    # Procesar respuesta
    if api_result.get("status") == "success" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"Producto con ID {producto_id} eliminado exitosamente."
    elif api_result.get("status") == "error" and "message_for_user" not in api_result:
        api_result["message_for_user"] = f"No pude eliminar el producto con ID {producto_id}. Error: {api_result.get('message', 'desconocido')}."
    
    return api_result

# Lista de herramientas disponibles para el agente
PRODUCTO_AGENT_TOOLS = [
    list_productos,
    get_producto,
    create_producto,
    update_producto,
    delete_producto
]