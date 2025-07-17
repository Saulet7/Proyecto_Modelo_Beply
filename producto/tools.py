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

def get_producto(tool_context, producto_input: str):
    """
    Obtiene información de uno o varios productos según ID, referencia exacta o descripción parcial.

    Args:
        producto_input (str): ID del producto, referencia exacta o parte de la descripción a buscar.
    """
    logger.info(f"TOOL EXECUTED: get_producto_by_referencia(producto_input='{producto_input}')")

    def es_numero(valor: str) -> bool:
        """Verifica si el valor es un número (ID de producto)"""
        return valor.isdigit()

    try:
        if es_numero(producto_input):
            # Buscar directamente por ID
            api_result = make_fs_request("GET", f"/productos/{producto_input}")
            if api_result.get("status") == "success":
                producto_data = api_result.get("data", {})
                if producto_data:
                    return {
                        "status": "success",
                        "data": {
                            "idproducto": producto_data.get("idproducto"),
                            "referencia": producto_data.get("referencia"),
                            "descripcion": producto_data.get("descripcion"),
                            "precio": producto_data.get("precio"),
                            "codfamilia": producto_data.get("codfamilia"),
                            "codfabricante": producto_data.get("codfabricante"),
                            "status": "found"
                        },
                        "message_for_user": f"Producto encontrado: '{producto_data.get('descripcion')}' (Ref: {producto_data.get('referencia')}) - ID: {producto_data.get('idproducto')}."
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Producto no encontrado",
                        "message_for_user": f"No se encontró un producto con ID '{producto_input}'."
                    }

        # Buscar por referencia exacta o descripción parcial (listado + filtro)
        all_result = make_fs_request("GET", "/productos")
        if all_result.get("status") != "success":
            return {
                "status": "error",
                "message": "Error al obtener lista de productos",
                "message_for_user": "No pude obtener la lista de productos para buscar coincidencias."
            }

        productos = all_result.get("data", [])
        
        # Primero buscar por referencia exacta
        coincidencias_exactas = [
            {
                "idproducto": p.get("idproducto"),
                "referencia": p.get("referencia"),
                "descripcion": p.get("descripcion"),
                "precio": p.get("precio"),
                "codfamilia": p.get("codfamilia"),
                "codfabricante": p.get("codfabricante"),
                "status": "found"
            }
            for p in productos
            if producto_input.upper() == (p.get("referencia") or "").upper()
        ]

        if coincidencias_exactas:
            if len(coincidencias_exactas) == 1:
                producto = coincidencias_exactas[0]
                return {
                    "status": "success",
                    "data": producto,
                    "message_for_user": f"Producto encontrado por referencia: '{producto['descripcion']}' (Ref: {producto['referencia']}) - ID: {producto['idproducto']}."
                }
            else:
                return {
                    "status": "multiple",
                    "data": coincidencias_exactas,
                    "message_for_user": f"Se encontraron {len(coincidencias_exactas)} productos con referencia '{producto_input}'."
                }

        # Si no hay coincidencias exactas, buscar por descripción parcial
        coincidencias_descripcion = [
            {
                "idproducto": p.get("idproducto"),
                "referencia": p.get("referencia"),
                "descripcion": p.get("descripcion"),
                "precio": p.get("precio"),
                "codfamilia": p.get("codfamilia"),
                "codfabricante": p.get("codfabricante"),
                "status": "found"
            }
            for p in productos
            if producto_input.lower() in (p.get("descripcion") or "").lower()
        ]

        if len(coincidencias_descripcion) == 1:
            producto = coincidencias_descripcion[0]
            return {
                "status": "success",
                "data": producto,
                "message_for_user": f"Producto encontrado por descripción: '{producto['descripcion']}' (Ref: {producto['referencia']}) - ID: {producto['idproducto']}."
            }
        elif len(coincidencias_descripcion) > 1:
            return {
                "status": "multiple",
                "data": coincidencias_descripcion,
                "message_for_user": f"Se encontraron {len(coincidencias_descripcion)} productos que coinciden con '{producto_input}' en la descripción. Por favor, especifica la referencia exacta si es posible."
            }
        else:
            return {
                "status": "not_found",
                "message": "No hay coincidencias",
                "message_for_user": f"No se encontró ningún producto que contenga '{producto_input}' en su referencia o descripción."
            }

    except Exception as e:
        logger.error(f"Error al obtener producto '{producto_input}': {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al obtener el producto '{producto_input}': {str(e)}"
        }

# Lista de herramientas disponibles para el agente
PRODUCTO_AGENT_TOOLS = [
    list_productos,
    get_producto,
    create_producto,
    update_producto,
    delete_producto,
    get_producto
]