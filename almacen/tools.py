import logging
from typing import Optional, Any
from utils import make_fs_request

logger = logging.getLogger(__name__)

# --- ALMACENES ---
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

def upsert_warehouse(
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
    apartado: str,
    id: Optional[str] = None
):
    logger.info(f"TOOL EXECUTED: upsert_warehouse(codalmacen='{codalmacen}')")

    # Validación estricta de campos requeridos
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

    form_data = required_fields.copy()
    method = "POST"
    path = "/almacenes"

    if id:
        method = "PUT"
        path = f"/almacenes/{id}"

    try:
        api_result = make_fs_request(method, path, data=form_data)
        if api_result.get("status") == "success":
            api_result.setdefault("message_for_user", f"Almacén '{codalmacen}' guardado correctamente.")
        else:
            api_result.setdefault("message_for_user", f"No se pudo guardar el almacén '{codalmacen}'.")
        return api_result
    except Exception as e:
        logger.error(f"Error en upsert_warehouse: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al guardar el almacén: {str(e)}"
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

# --- ATRIBUTOS DE PRODUCTO ---
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

def upsert_attribute(tool_context, nombre: str, tipo: str, **kwargs):
    logger.info(f"TOOL EXECUTED: upsert_attribute(nombre='{nombre}', tipo='{tipo}')")
    if not nombre or not tipo:
        return {
            "status": "error",
            "message": "Nombre y tipo son obligatorios.",
            "message_for_user": "Debes indicar el nombre y tipo del atributo."
        }
    method = "POST"
    path = "/atributos"
    if kwargs.get("id"):
        method = "PUT"
        path = f"/atributos/{kwargs.pop('id')}"
    data = {"nombre": nombre, "tipo": tipo}
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

# --- FABRICANTES ---
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

def upsert_manufacturer(tool_context, nombre: str, **kwargs):
    logger.info(f"TOOL EXECUTED: upsert_manufacturer(nombre='{nombre}')")
    if not nombre:
        return {
            "status": "error",
            "message": "El nombre del fabricante es obligatorio.",
            "message_for_user": "Debes indicar el nombre del fabricante."
        }
    method = "POST"
    path = "/fabricantes"
    if kwargs.get("id"):
        method = "PUT"
        path = f"/fabricantes/{kwargs.pop('id')}"
    data = {"nombre": nombre}
    data.update(kwargs)
    try:
        api_result = make_fs_request(method, path, data=data)
        if api_result.get("status") == "success":
            api_result.setdefault("message_for_user", f"Fabricante '{nombre}' guardado correctamente.")
        else:
            api_result.setdefault("message_for_user", f"No se pudo guardar el fabricante '{nombre}'.")
        return api_result
    except Exception as e:
        logger.error(f"Error en upsert_manufacturer: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al guardar el fabricante: {str(e)}"
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


# --- FAMILIAS ---

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

def upsert_family(tool_context, codigo: str, descripcion: str, **kwargs):
    logger.info(f"TOOL EXECUTED: upsert_family(codigo='{codigo}', descripcion='{descripcion}')")
    if not codigo or not descripcion:
        return {
            "status": "error",
            "message": "Código y descripción son obligatorios.",
            "message_for_user": "Debes indicar el código y la descripción de la familia."
        }
    method = "POST"
    path = "/familias"
    if kwargs.get("id"):
        method = "PUT"
        path = f"/familias/{kwargs.pop('id')}"
    data = {"codigo": codigo, "descripcion": descripcion}
    data.update(kwargs)
    try:
        api_result = make_fs_request(method, path, data=data)
        if api_result.get("status") == "success":
            api_result.setdefault("message_for_user", f"Familia '{codigo}' guardada correctamente.")
        else:
            api_result.setdefault("message_for_user", f"No se pudo guardar la familia '{codigo}'.")
        return api_result
    except Exception as e:
        logger.error(f"Error en upsert_family: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al guardar la familia: {str(e)}"
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

def upsert_product(tool_context, codigo: str, descripcion: str, **kwargs):
    logger.info(f"TOOL EXECUTED: upsert_product(codigo='{codigo}', descripcion='{descripcion}')")
    if not codigo or not descripcion:
        return {
            "status": "error",
            "message": "Código y descripción son obligatorios.",
            "message_for_user": "Debes indicar el código y la descripción del producto."
        }
    method = "POST"
    path = "/productos"
    if kwargs.get("id"):
        method = "PUT"
        path = f"/productos/{kwargs.pop('id')}"
    data = {"codigo": codigo, "descripcion": descripcion}
    data.update(kwargs)
    try:
        api_result = make_fs_request(method, path, data=data)
        if api_result.get("status") == "success":
            api_result.setdefault("message_for_user", f"Producto '{codigo}' guardado correctamente.")
        else:
            api_result.setdefault("message_for_user", f"No se pudo guardar el producto '{codigo}'.")
        return api_result
    except Exception as e:
        logger.error(f"Error en upsert_product: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al guardar el producto: {str(e)}"
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
    upsert_warehouse,
    delete_warehouse,
    list_manufacturers,
    upsert_manufacturer,
    delete_manufacturer,
    list_families,
    upsert_family,
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


