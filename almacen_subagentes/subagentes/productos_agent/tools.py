import logging
from typing import Optional, Any
from utils import make_fs_request

logger = logging.getLogger(__name__)

def list_products(tool_context, **filters):
    logger.info(f"TOOL EXECUTED: list_products(filters={filters})")
    try:
        api_result = make_fs_request("GET", "/productos", params=filters)
        if api_result.get("status") == "success":
            data = api_result.get("data", [])
            api_result.setdefault("message_for_user", f"Se encontraron {len(data)} productos.")
        else:
            api_result.setdefault("message_for_user", "No se pudo obtener la lista de productos.")
        return api_result
    except Exception as e:
        logger.error(f"Error en list_products: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al listar productos: {str(e)}"
        }

def create_product(tool_context, referencia: str, descripcion: str, precio: float, **kwargs):
    logger.info(f"TOOL EXECUTED: create_product(referencia='{referencia}', descripcion='{descripcion}', precio={precio})")

    if not referencia or not descripcion or precio is None:
        return {
            "status": "error",
            "message": "Referencia, descripción y precio son obligatorios.",
            "message_for_user": "Debes indicar la referencia, descripción y precio del producto."
        }

    producto = {
        "referencia": referencia,
        "descripcion": descripcion,
        "precio": precio
    }
    producto.update(kwargs)

    # ⚠️ Convertir booleanos a enteros (1 / 0)
    for k, v in producto.items():
        if isinstance(v, bool):
            producto[k] = int(v)

    try:
        response = make_fs_request("POST", "/productos", data=producto)
        if response.get("status") == "success":
            response.setdefault("message_for_user", f"Producto '{referencia}' creado correctamente.")
        else:
            response.setdefault("message_for_user", f"No se pudo crear el producto '{referencia}'.")
        return response
    except Exception as e:
        logger.error(f"Error en create_product: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al crear el producto: {str(e)}"
        }

def update_product(tool_context, referencia: str, **kwargs):
    logger.info(f"TOOL EXECUTED: update_product(referencia='{referencia}', cambios={kwargs})")

    if not referencia:
        return {
            "status": "error",
            "message": "La referencia es obligatoria.",
            "message_for_user": "Debes indicar la referencia del producto que quieres modificar."
        }

    try:
        # Buscar producto exacto por referencia
        search_result = make_fs_request("GET", "/productos", params={"referencia": referencia})
        productos = search_result.get("data", [])

        # Filtrar por coincidencia exacta
        productos_filtrados = [
            p for p in productos if p.get("referencia", "").strip().lower() == referencia.strip().lower()
        ]

        if not productos_filtrados:
            return {
                "status": "error",
                "message": f"No se encontró ningún producto con referencia exacta '{referencia}'.",
                "message_for_user": f"No existe ningún producto con la referencia '{referencia}'."
            }

        if len(productos_filtrados) > 1:
            logger.warning(f"Varias coincidencias para referencia '{referencia}': usando la primera.")
        
        producto = productos_filtrados[0]
        producto_id = producto.get("idproducto")

        if not producto_id:
            return {
                "status": "error",
                "message": "No se encontró ID válido para el producto.",
                "message_for_user": "No se pudo identificar correctamente el producto a modificar."
            }

        if not kwargs:
            return {
                "status": "error",
                "message": "No se proporcionaron campos para actualizar.",
                "message_for_user": "Debes indicar al menos un campo que quieras modificar del producto."
            }

        # Convertir booleanos a enteros
        for k, v in kwargs.items():
            if isinstance(v, bool):
                kwargs[k] = int(v)

        response = make_fs_request("PUT", f"/productos/{producto_id}", data=kwargs)

        if response.get("status") == "success":
            response.setdefault("message_for_user", f"Producto '{referencia}' actualizado correctamente.")
        else:
            response.setdefault("message_for_user", f"No se pudo actualizar el producto '{referencia}'.")

        return response

    except Exception as e:
        logger.error(f"Error en update_product: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al modificar el producto '{referencia}': {str(e)}"
        }

def delete_product(tool_context, product_id: str):
    logger.info(f"TOOL EXECUTED: delete_product(product_id='{product_id}')")
    if not product_id:
        return {
            "status": "error",
            "message": "ID del producto requerido.",
            "message_for_user": "Debes proporcionar el ID del producto a eliminar."
        }
    try:
        api_result = make_fs_request("DELETE", f"/productos/{product_id}")
        if api_result.get("status") == "success":
            api_result.setdefault("message_for_user", f"Producto con ID '{product_id}' eliminado correctamente.")
        else:
            api_result.setdefault("message_for_user", f"No se pudo eliminar el producto con ID '{product_id}'.")
        return api_result
    except Exception as e:
        logger.error(f"Error en delete_product: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al eliminar el producto: {str(e)}"
        }


AGENT_TOOLS = [
    list_products,
    create_product,
    update_product,
    delete_product
]
