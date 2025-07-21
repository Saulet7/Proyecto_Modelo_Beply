import logging
from typing import Optional, Any
from utils import make_fs_request

logger = logging.getLogger(__name__)

# --- ALMACENES ---> listo
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

# --- ATRIBUTOS DE PRODUCTO ---> listo
def list_attributes(tool_context):
    logger.info("TOOL EXECUTED: list_attributes()")
    try:
        api_result = make_fs_request("GET", "/atributos")
        if api_result.get("status") == "success":
            data = api_result.get("data", [])
            api_result.setdefault("message_for_user", f"Se encontraron {len(data)} atributos.")
        else:
            api_result.setdefault("message_for_user", "No se pudo obtener la lista de atributos.")
        return api_result
    except Exception as e:
        logger.error(f"Error en list_attributes: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al listar atributos: {str(e)}"
        }

def upsert_attribute(tool_context, nombre: str, **kwargs):
    logger.info(f"TOOL EXECUTED: upsert_attribute(nombre='{nombre}'')")
    if not nombre:
        return {
            "status": "error",
            "message": "Nombre obligatorios.",
            "message_for_user": "Debes indicar el nombre y tipo del atributo."
        }
    method = "POST"
    path = "/atributos"
    if kwargs.get("id"):
        method = "PUT"
        path = f"/atributos/{kwargs.pop('id')}"
    data = {"nombre": nombre}
    data.update(kwargs)
    try:
        api_result = make_fs_request(method, path, data=data)
        if api_result.get("status") == "success":
            api_result.setdefault("message_for_user", f"Atributo '{nombre}' guardado correctamente.")
        else:
            api_result.setdefault("message_for_user", f"No se pudo guardar el atributo '{nombre}'.")
        return api_result
    except Exception as e:
        logger.error(f"Error en upsert_attribute: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al guardar el atributo: {str(e)}"
        }

def delete_attribute(tool_context, attribute_id: str):
    logger.info(f"TOOL EXECUTED: delete_attribute(attribute_id='{attribute_id}')")
    if not attribute_id:
        return {
            "status": "error",
            "message": "ID del atributo requerido.",
            "message_for_user": "Debes proporcionar el ID del atributo a eliminar."
        }
    try:
        api_result = make_fs_request("DELETE", f"/atributos/{attribute_id}")
        if api_result.get("status") == "success":
            api_result.setdefault("message_for_user", f"Atributo con ID '{attribute_id}' eliminado correctamente.")
        else:
            api_result.setdefault("message_for_user", f"No se pudo eliminar el atributo con ID '{attribute_id}'.")
        return api_result
    except Exception as e:
        logger.error(f"Error en delete_attribute: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al eliminar el atributo: {str(e)}"
        }

# DUDAS DE COMO HACERLO, EJEMPLO DE COMO SERÍA LA TOOL
def assign_attribute_to_product(tool_context, producto_id: str, atributo_id: str, valor: str):
    logger.info(f"TOOL EXECUTED: assign_attribute_to_product(producto_id='{producto_id}', atributo_id='{atributo_id}', valor='{valor}')")
    if not producto_id or not atributo_id:
        return {
            "status": "error",
            "message": "Faltan datos obligatorios (producto_id, atributo_id).",
            "message_for_user": "Debes indicar el producto y el atributo a asignar."
        }
    form_data = {
        "producto_id": producto_id,
        "atributo_id": atributo_id,
        "valor": valor
    }
    try:
        api_result = make_fs_request("POST", "/atributosproductos", data=form_data)
        if api_result.get("status") == "success":
            api_result.setdefault("message_for_user", f"Atributo asignado correctamente al producto.")
        else:
            api_result.setdefault("message_for_user", "No se pudo asignar el atributo al producto.")
        return api_result
    except Exception as e:
        logger.error(f"Error en assign_attribute_to_product: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al asignar el atributo al producto: {str(e)}"
        }

# --- FABRICANTES ---> listo
def list_manufacturers(tool_context):
    logger.info("TOOL EXECUTED: list_manufacturers()")
    try:
        api_result = make_fs_request("GET", "/fabricantes")
        if api_result.get("status") == "success":
            data = api_result.get("data", [])
            api_result.setdefault("message_for_user", f"Se encontraron {len(data)} fabricantes.")
        else:
            api_result.setdefault("message_for_user", "No se pudo obtener la lista de fabricantes.")
        return api_result
    except Exception as e:
        logger.error(f"Error en list_manufacturers: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al listar fabricantes: {str(e)}"
        }

def create_manufacturer(tool_context, nombre: str, **kwargs):
    logger.info(f"TOOL EXECUTED: create_manufacturer(nombre='{nombre}')")
    
    if not nombre:
        return {
            "status": "error",
            "message": "El nombre del fabricante es obligatorio.",
            "message_for_user": "Debes indicar el nombre del fabricante."
        }

    data = {"nombre": nombre}
    data.update(kwargs)

    try:
        response = make_fs_request("POST", "/fabricantes", data=data)
        if response.get("status") == "success":
            response.setdefault("message_for_user", f"Fabricante '{nombre}' creado correctamente.")
        else:
            response.setdefault("message_for_user", f"No se pudo crear el fabricante '{nombre}'.")
        return response
    except Exception as e:
        logger.error(f"Error en create_manufacturer: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al crear el fabricante: {str(e)}"
        }

def update_manufacturer(tool_context, id: str, **kwargs):
    logger.info(f"TOOL EXECUTED: update_manufacturer(id='{id}')")

    if not id:
        return {
            "status": "error",
            "message": "El ID del fabricante es obligatorio para actualizar.",
            "message_for_user": "Debes indicar el ID del fabricante a modificar."
        }

    if not kwargs:
        return {
            "status": "error",
            "message": "No se proporcionaron campos para actualizar.",
            "message_for_user": "Debes indicar al menos un campo para modificar del fabricante."
        }

    try:
        response = make_fs_request("PUT", f"/fabricantes/{id}", data=kwargs)
        if response.get("status") == "success":
            response.setdefault("message_for_user", f"Fabricante actualizado correctamente.")
        else:
            response.setdefault("message_for_user", f"No se pudo actualizar el fabricante.")
        return response
    except Exception as e:
        logger.error(f"Error en update_manufacturer: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al actualizar el fabricante: {str(e)}"
        }

def delete_manufacturer(tool_context, manufacturer_id: str):
    logger.info(f"TOOL EXECUTED: delete_manufacturer(manufacturer_id='{manufacturer_id}')")
    if not manufacturer_id:
        return {
            "status": "error",
            "message": "ID del fabricante requerido.",
            "message_for_user": "Debes proporcionar el ID del fabricante a eliminar."
        }
    try:
        api_result = make_fs_request("DELETE", f"/fabricantes/{manufacturer_id}")
        if api_result.get("status") == "success":
            api_result.setdefault("message_for_user", f"Fabricante con ID '{manufacturer_id}' eliminado correctamente.")
        else:
            api_result.setdefault("message_for_user", f"No se pudo eliminar el fabricante con ID '{manufacturer_id}'.")
        return api_result
    except Exception as e:
        logger.error(f"Error en delete_manufacturer: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al eliminar el fabricante: {str(e)}"
        }


# --- FAMILIAS ---> listo

def list_families(tool_context):
    logger.info("TOOL EXECUTED: list_families()")
    try:
        api_result = make_fs_request("GET", "/familias")
        if api_result.get("status") == "success":
            data = api_result.get("data", [])
            api_result.setdefault("message_for_user", f"Se encontraron {len(data)} familias.")
        else:
            api_result.setdefault("message_for_user", "No se pudo obtener la lista de familias.")
        return api_result
    except Exception as e:
        logger.error(f"Error en list_families: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al listar familias: {str(e)}"
        }

def create_family(tool_context, codigo: str, descripcion: str, **kwargs):
    logger.info(f"TOOL EXECUTED: create_family(codigo='{codigo}', descripcion='{descripcion}')")

    if not codigo or not descripcion:
        return {
            "status": "error",
            "message": "Código y descripción son obligatorios.",
            "message_for_user": "Debes indicar el código y la descripción de la familia."
        }

    data = {"codigo": codigo, "descripcion": descripcion}
    data.update(kwargs)

    try:
        response = make_fs_request("POST", "/familias", data=data)
        if response.get("status") == "success":
            response.setdefault("message_for_user", f"Familia '{codigo}' creada correctamente.")
        else:
            response.setdefault("message_for_user", f"No se pudo crear la familia '{codigo}'.")
        return response
    except Exception as e:
        logger.error(f"Error en create_family: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al crear la familia: {str(e)}"
        }

def update_family(tool_context, id: str, **kwargs):
    logger.info(f"TOOL EXECUTED: update_family(id='{id}')")

    if not id:
        return {
            "status": "error",
            "message": "El ID de la familia es obligatorio para actualizar.",
            "message_for_user": "Debes indicar el ID de la familia que deseas modificar."
        }

    if not kwargs:
        return {
            "status": "error",
            "message": "No se proporcionaron campos para actualizar.",
            "message_for_user": "Debes indicar al menos un campo para modificar en la familia."
        }

    try:
        response = make_fs_request("PUT", f"/familias/{id}", data=kwargs)
        if response.get("status") == "success":
            response.setdefault("message_for_user", f"Familia actualizada correctamente.")
        else:
            response.setdefault("message_for_user", f"No se pudo actualizar la familia.")
        return response
    except Exception as e:
        logger.error(f"Error en update_family: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al actualizar la familia: {str(e)}"
        }

def delete_family(tool_context, family_id: str):
    logger.info(f"TOOL EXECUTED: delete_family(family_id='{family_id}')")
    if not family_id:
        return {
            "status": "error",
            "message": "ID de la familia requerido.",
            "message_for_user": "Debes proporcionar el ID de la familia a eliminar."
        }
    try:
        api_result = make_fs_request("DELETE", f"/familias/{family_id}")
        if api_result.get("status") == "success":
            api_result.setdefault("message_for_user", f"Familia con ID '{family_id}' eliminada correctamente.")
        else:
            api_result.setdefault("message_for_user", f"No se pudo eliminar la familia con ID '{family_id}'.")
        return api_result
    except Exception as e:
        logger.error(f"Error en delete_family: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al eliminar la familia: {str(e)}"
        }

# --- PRODUCTOS ---

def list_products(tool_context):
    logger.info("TOOL EXECUTED: list_products()")
    try:
        api_result = make_fs_request("GET", "/productos")
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

def upsert_product(tool_context, referencia: str, **kwargs):
    logger.info(f"TOOL EXECUTED: upsert_product(referencia='{referencia}', cambios={kwargs})")

    if not referencia:
        return {
            "status": "error",
            "message": "La referencia es obligatoria.",
            "message_for_user": "Debes indicar la referencia del producto que quieres modificar."
        }

    try:
        # Buscar producto por referencia
        search_result = make_fs_request("GET", "/productos", params={"referencia": referencia})
        productos = search_result.get("data", [])

        if not productos:
            return {
                "status": "error",
                "message": f"No se encontró ningún producto con referencia '{referencia}'.",
                "message_for_user": f"No existe ningún producto con la referencia '{referencia}'."
            }

        # Producto encontrado
        producto = productos[0]
        producto_id = producto["idproducto"]

        # Actualizar solo los campos necesarios
        producto_actualizado = {**producto, **kwargs}

        # ⚠️ Convertir booleanos a enteros (1 / 0)
        for clave, valor in producto_actualizado.items():
            if isinstance(valor, bool):
                producto_actualizado[clave] = int(valor)

        # Realizar el PUT
        api_result = make_fs_request("PUT", f"/productos/{producto_id}", data=producto_actualizado)

        if api_result.get("status") == "success":
            api_result.setdefault("message_for_user", f"Producto '{referencia}' actualizado correctamente.")
        else:
            api_result.setdefault("message_for_user", f"No se pudo actualizar el producto '{referencia}'.")

        return api_result

    except Exception as e:
        logger.error(f"Error en upsert_product: {e}", exc_info=True)
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

# --- STOCK ---

def list_stock(tool_context):
    logger.info("TOOL EXECUTED: list_stock()")
    try:
        api_result = make_fs_request("GET", "/stocks")
        if api_result.get("status") == "success":
            stock = api_result.get("data", [])
            api_result.setdefault("message_for_user", f"Se encontraron {len(stock)} registros de stock.")
        else:
            api_result.setdefault("message_for_user", "No se pudo obtener el stock.")
        return api_result
    except Exception as e:
        logger.error(f"Error en list_stock: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al consultar el stock: {str(e)}"
        }

def adjust_stock(tool_context, codproducto: str, cantidad: int, motivo: Optional[str] = None):
    logger.info(f"TOOL EXECUTED: adjust_stock(codproducto='{codproducto}', cantidad={cantidad})")
    if not codproducto:
        return {
            "status": "error",
            "message": "Código de producto requerido.",
            "message_for_user": "Debes proporcionar el código del producto a ajustar."
        }
    data = {"codproducto": codproducto, "cantidad": cantidad}
    if motivo:
        data["motivo"] = motivo
    try:
        api_result = make_fs_request("POST", "/stocks/adjust", data=data)
        if api_result.get("status") == "success":
            api_result.setdefault("message_for_user", f"Stock de '{codproducto}' ajustado correctamente.")
        else:
            api_result.setdefault("message_for_user", f"No se pudo ajustar el stock de '{codproducto}'.")
        return api_result
    except Exception as e:
        logger.error(f"Error en adjust_stock: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al ajustar el stock: {str(e)}"
        }

def transfer_stock(tool_context, codproducto: str, desde: str, hacia: str, cantidad: int):
    logger.info(f"TOOL EXECUTED: transfer_stock(codproducto='{codproducto}', desde='{desde}', hacia='{hacia}', cantidad={cantidad})")
    if not all([codproducto, desde, hacia, cantidad]):
        return {
            "status": "error",
            "message": "Datos incompletos para transferencia.",
            "message_for_user": "Debes indicar producto, almacenes origen/destino y cantidad."
        }
    data = {
        "codproducto": codproducto,
        "desde": desde,
        "hacia": hacia,
        "cantidad": cantidad
    }
    try:
        api_result = make_fs_request("POST", "/stocks/transfer", data=data)
        if api_result.get("status") == "success":
            api_result.setdefault("message_for_user", f"Transferencia de {cantidad} unidades de '{codproducto}' realizada.")
        else:
            api_result.setdefault("message_for_user", "No se pudo realizar la transferencia de stock.")
        return api_result
    except Exception as e:
        logger.error(f"Error en transfer_stock: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al transferir el stock: {str(e)}"
        }

def stock_history(tool_context, codproducto: str):
    logger.info(f"TOOL EXECUTED: stock_history(codproducto='{codproducto}')")
    if not codproducto:
        return {
            "status": "error",
            "message": "Código de producto requerido.",
            "message_for_user": "Debes proporcionar el código del producto para consultar su historial."
        }
    try:
        api_result = make_fs_request("GET", f"/stocks/history?codproducto={codproducto}")
        if api_result.get("status") == "success":
            movimientos = api_result.get("data", [])
            api_result.setdefault("message_for_user", f"Historial con {len(movimientos)} movimientos para '{codproducto}'.")
        else:
            api_result.setdefault("message_for_user", "No se pudo obtener el historial de stock.")
        return api_result
    except Exception as e:
        logger.error(f"Error en stock_history: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al consultar el historial: {str(e)}"
        }

# --- TRANSPORTISTAS ---

def list_carriers(tool_context):
    logger.info("TOOL EXECUTED: list_carriers()")
    try:
        api_result = make_fs_request("GET", "/agenciatransportes")
        if api_result.get("status") == "success":
            data = api_result.get("data", [])
            api_result.setdefault("message_for_user", f"Se encontraron {len(data)} transportistas.")
        else:
            api_result.setdefault("message_for_user", "No se pudo obtener la lista de transportistas.")
        return api_result
    except Exception as e:
        logger.error(f"Error en list_carriers: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al listar transportistas: {str(e)}"
        }

def upsert_carrier(tool_context, nombre: str, **kwargs):
    logger.info(f"TOOL EXECUTED: upsert_carrier(nombre='{nombre}')")
    if not nombre:
        return {
            "status": "error",
            "message": "El nombre es obligatorio.",
            "message_for_user": "Debes indicar el nombre del transportista."
        }
    method = "POST"
    path = "/agenciatransportes"
    if kwargs.get("id"):
        method = "PUT"
        path = f"/agenciatransportes/{kwargs.pop('id')}"
    data = {"nombre": nombre}
    data.update(kwargs)
    try:
        api_result = make_fs_request(method, path, data=data)
        if api_result.get("status") == "success":
            api_result.setdefault("message_for_user", f"Transportista '{nombre}' guardado correctamente.")
        else:
            api_result.setdefault("message_for_user", f"No se pudo guardar el transportista '{nombre}'.")
        return api_result
    except Exception as e:
        logger.error(f"Error en upsert_carrier: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al guardar el transportista: {str(e)}"
        }

def delete_carrier(tool_context, carrier_id: str):
    logger.info(f"TOOL EXECUTED: delete_carrier(carrier_id='{carrier_id}')")
    if not carrier_id:
        return {
            "status": "error",
            "message": "ID del transportista requerido.",
            "message_for_user": "Debes proporcionar el ID del transportista a eliminar."
        }
    try:
        api_result = make_fs_request("DELETE", f"/agenciatransportes/{carrier_id}")
        if api_result.get("status") == "success":
            api_result.setdefault("message_for_user", f"Transportista con ID '{carrier_id}' eliminado correctamente.")
        else:
            api_result.setdefault("message_for_user", f"No se pudo eliminar el transportista con ID '{carrier_id}'.")
        return api_result
    except Exception as e:
        logger.error(f"Error en delete_carrier: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al eliminar el transportista: {str(e)}"
        }

# --- GENERADOR DE REPOSTES ---
def generate_sales_report(tool_context, fecha_inicio: str, fecha_fin: str, 
                          codproducto: str = "", codfamilia: str = "", 
                          codtransportista: str = "", formato: str = "csv"):
    
    logger.info(f"TOOL EXECUTED: generate_sales_report(fecha_inicio='{fecha_inicio}', fecha_fin='{fecha_fin}', "
                f"codproducto='{codproducto}', codfamilia='{codfamilia}', codtransportista='{codtransportista}', formato='{formato}')")

    # Validaciones básicas
    if not fecha_inicio or not fecha_fin:
        return {
            "status": "error",
            "message": "Se requieren fecha_inicio y fecha_fin.",
            "message_for_user": "Debes proporcionar fecha de inicio y fin para el informe de ventas."
        }
    if formato not in ("csv", "xlsx"):
        return {
            "status": "error",
            "message": "Formato no válido. Solo se acepta 'csv' o 'xlsx'.",
            "message_for_user": "El formato debe ser 'csv' o 'xlsx'."
        }

    payload = {
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "formato": formato
    }
    if codproducto:
        payload["codproducto"] = codproducto
    if codfamilia:
        payload["codfamilia"] = codfamilia
    if codtransportista:
        payload["codtransportista"] = codtransportista

    try:
        api_result = make_fs_request("POST", "/informes/ventas", json=payload)
        if api_result.get("status") == "success":
            api_result.setdefault("message_for_user", "Informe de ventas generado correctamente.")
        else:
            api_result.setdefault("message_for_user", "No se pudo generar el informe de ventas.")
        return api_result

    except Exception as e:
        logger.error(f"Error en generate_sales_report: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al generar el informe de ventas: {str(e)}"
        }


ALMACEN_AGENT_TOOLS = [
    list_attributes,
    upsert_attribute,
    delete_attribute,
    assign_attribute_to_product,
    list_warehouses,
    # upsert_warehouse,
    update_warehouse, # separacion de upsert: actualizar almacén existente
    create_warehouse, # separacion de upsert: crear almacén nuevo
    delete_warehouse,
    list_manufacturers,
    #upsert_manufacturer,
    create_manufacturer, # separacion de upsert: actualizar fabricante existente
    update_manufacturer, # separacion de upsert: crear fabricante nuevo
    delete_manufacturer,
    list_families,
    # upsert_family,
    create_family, # separacion de upsert: actualizar family existente
    update_family, # separacion de upsert: crear family nuevo
    delete_family,
    list_products,
    upsert_product,
    delete_product,
    list_stock,
    adjust_stock,
    transfer_stock,
    stock_history,
    list_carriers,
    upsert_carrier,
    delete_carrier,
    generate_sales_report,
]


