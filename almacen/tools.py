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
def list_attributes(tool_context, **filters):
    logger.info(f"TOOL EXECUTED: list_attributes(filters={filters})")

    try:
        # Extraer filtros especiales para relaciones atributo-producto
        valor = filters.pop("valor", None)
        codproducto = filters.pop("codproducto", None)
        idproducto = filters.pop("idproducto", None)

        # 1. Obtener lista de atributos (filtrar solo por atributos propios)
        atributos_result = make_fs_request("GET", "/atributos", params=filters)
        if atributos_result.get("status") != "success":
            return {
                "status": "error",
                "message": "No se pudo obtener la lista de atributos.",
                "message_for_user": "No se pudo obtener la lista de atributos."
            }

        atributos = atributos_result.get("data", [])

        # 2. Obtener relaciones atributo-producto
        # Si hay filtros de producto, aplicarlos directamente en la consulta si la API lo soporta
        relaciones_params = {}
        if codproducto:
            relaciones_params["codproducto"] = codproducto
        if idproducto:
            relaciones_params["idproducto"] = idproducto
        if valor:
            relaciones_params["valor"] = valor

        relaciones_result = make_fs_request("GET", "/atributovalores", params=relaciones_params)
        if relaciones_result.get("status") != "success":
            return {
                "status": "error",
                "message": "No se pudieron obtener las asignaciones de atributos.",
                "message_for_user": "No se pudieron obtener las asignaciones de atributos a productos."
            }

        relaciones = relaciones_result.get("data", [])

        # 3. Si no se pudieron aplicar filtros en la API, filtrar manualmente
        if not relaciones_params:  # Solo si no se aplicaron filtros en la consulta
            relaciones_filtradas = []
            for r in relaciones:
                if (not valor or r.get("valor") == valor) and \
                   (not codproducto or r.get("codproducto") == codproducto) and \
                   (not idproducto or r.get("idproducto") == int(idproducto) if idproducto else True):
                    relaciones_filtradas.append(r)
        else:
            relaciones_filtradas = relaciones

        # 4. Crear diccionario de asignaciones por codatributo
        from collections import defaultdict
        asignaciones_por_atributo = defaultdict(list)
        
        for relacion in relaciones_filtradas:
            codatributo = relacion.get("codatributo")
            if codatributo:
                asignaciones_por_atributo[codatributo].append({
                    "codproducto": relacion.get("codproducto"),
                    "idproducto": relacion.get("idproducto"),
                    "valor": relacion.get("valor")
                })

        # 5. Enriquecer atributos con sus asignaciones
        atributos_enriquecidos = []
        
        for atributo in atributos:
            codatributo = atributo.get("codatributo")
            asignaciones = asignaciones_por_atributo.get(codatributo, [])
            
            # Agregar asignaciones al atributo
            atributo_copia = atributo.copy()
            atributo_copia["asignaciones"] = asignaciones
            
            # Decidir si incluir el atributo basado en los filtros
            incluir_atributo = True
            
            # Si hay filtros de relación (valor, codproducto, idproducto)
            if valor or codproducto or idproducto:
                # Solo incluir si tiene asignaciones que coincidan con los filtros
                incluir_atributo = len(asignaciones) > 0
            
            if incluir_atributo:
                atributos_enriquecidos.append(atributo_copia)

        # 6. Mensaje personalizado según el contexto
        if codproducto:
            mensaje_usuario = f"Se encontraron {len(atributos_enriquecidos)} atributos asignados al producto '{codproducto}'."
        elif valor:
            mensaje_usuario = f"Se encontraron {len(atributos_enriquecidos)} atributos con valor '{valor}'."
        else:
            mensaje_usuario = f"Se encontraron {len(atributos_enriquecidos)} atributos."

        return {
            "status": "success",
            "data": atributos_enriquecidos,
            "message": f"Se procesaron {len(atributos)} atributos y se encontraron {len(atributos_enriquecidos)} que coinciden con los filtros.",
            "message_for_user": mensaje_usuario
        }

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

def assign_attribute_to_product(tool_context, codproducto: str, codatributo: str, valor: str):
    logger.info(f"TOOL EXECUTED: assign_attribute_to_product(codproducto='{codproducto}', codatributo='{codatributo}', valor='{valor}')")
    
    if not codproducto or not codatributo:
        return {
            "status": "error",
            "message": "Faltan datos obligatorios (codproducto, codatributo).",
            "message_for_user": "Debes indicar el código del producto y el del atributo."
        }

    form_data = {
        "codproducto": str(codproducto),
        "codatributo": str(codatributo),
        "valor": valor
    }

    logger.debug(f"Enviando form_data a /atributovalor: {form_data}")

    try:
        api_result = make_fs_request("POST", "/atributovalores", data=form_data)
        if api_result.get("status") == "success":
            api_result.setdefault("message_for_user", f"Atributo '{codatributo}' asignado correctamente al producto '{codproducto}'.")
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

# --- PRODUCTOS ---> listo
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

# --- STOCK ---> listo

def list_stock(tool_context, **filters):
    """
    Filtros soportados:
        - codalmacen: str
        - idproducto: int
        - idfamilia: int
        - idfabricante: int
    """
    logger.info(f"TOOL EXECUTED: list_stock(filters={filters})")
    try:
        # Paso 1: Obtener todo el stock
        stock_response = make_fs_request("GET", "/stocks")
        if stock_response.get("status") != "success":
            stock_response.setdefault("message_for_user", "No se pudo obtener el stock.")
            return stock_response

        stock_data = stock_response.get("data", [])

        # Si hay filtros por producto, familia o fabricante, necesitamos los productos
        need_product_data = any(k in filters for k in ["idproducto", "idfamilia", "idfabricante"])

        if need_product_data:
            product_response = make_fs_request("GET", "/productos")
            if product_response.get("status") != "success":
                return {
                    "status": "error",
                    "message": "No se pudo obtener la lista de productos para aplicar los filtros.",
                    "message_for_user": "No se pudo aplicar filtros de familia o fabricante al stock."
                }
            productos = product_response.get("data", [])

            # Construimos un índice por idproducto
            productos_index = {p["idproducto"]: p for p in productos}

            # Filtrado cruzado
            stock_data = [
                s for s in stock_data
                if s.get("idproducto") in productos_index and
                   (not filters.get("idproducto") or s.get("idproducto") == filters["idproducto"]) and
                   (not filters.get("idfamilia") or productos_index[s["idproducto"]].get("idfamilia") == filters["idfamilia"]) and
                   (not filters.get("idfabricante") or productos_index[s["idproducto"]].get("idfabricante") == filters["idfabricante"])
            ]

        # Filtro directo por almacén (sin necesidad de productos)
        if "codalmacen" in filters:
            stock_data = [s for s in stock_data if s.get("codalmacen") == filters["codalmacen"]]

        stock_response["data"] = stock_data
        stock_response["message_for_user"] = f"Se encontraron {len(stock_data)} registros de stock tras aplicar los filtros."
        return stock_response

    except Exception as e:
        logger.error(f"Error en list_stock: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al consultar el stock: {str(e)}"
        }

def adjust_stock(tool_context, referencia: str, idproducto: int, codalmacen: str, cantidad: float, motivo: Optional[str] = None):
    logger.info(f"TOOL EXECUTED: adjust_stock(idproducto={idproducto}, codalmacen='{codalmacen}', cantidad={cantidad})")

    if not idproducto or not codalmacen:
        return {
            "status": "error",
            "message": "ID de producto y código de almacén son obligatorios.",
            "message_for_user": "Debes indicar el producto y el almacén donde ajustar el stock."
        }

    data = {
        "referencia": referencia,
        "idproducto": idproducto,
        "codalmacen": codalmacen,
        "cantidad": cantidad,
    }

    if motivo:
        data["motivo"] = motivo

    try:
        api_result = make_fs_request("POST", "/stocks/adjust", data=data)

        if api_result.get("status") == "success":
            api_result.setdefault("message_for_user", f"Stock del producto (ID {idproducto}) ajustado correctamente en almacén '{codalmacen}'.")
        else:
            api_result.setdefault("message_for_user", f"No se pudo ajustar el stock del producto en el almacén '{codalmacen}'.")

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

# --- TRANSPORTISTAS ---> listo

def list_carriers(tool_context, **filters):
    logger.info(f"TOOL EXECUTED: list_carriers(filters={filters})")
    try:
        api_result = make_fs_request("GET", "/agenciatransportes", params=filters)
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

def create_carrier(tool_context, nombre: str, codigo: str, telefono: str, web: str = "", activo: bool = True):
    logger.info(f"TOOL EXECUTED: create_carrier(nombre='{nombre}', codigo='{codigo}')")

    # Validación de campos obligatorios
    if not nombre or not codigo or not telefono:
        return {
            "status": "error",
            "message": "Faltan campos obligatorios: nombre, código o teléfono.",
            "message_for_user": "Debes indicar al menos el nombre, código y teléfono del transportista."
        }

    data = {
        "nombre": nombre,
        "codigo": codigo,
        "telefono": telefono,
        "web": web,
        "activo": int(activo)
    }

    try:
        api_result = make_fs_request("POST", "/agenciatransportes", data=data)
        if api_result.get("status") == "success":
            api_result.setdefault("message_for_user", f"Transportista '{nombre}' creado correctamente.")
        else:
            api_result.setdefault("message_for_user", f"No se pudo crear el transportista '{nombre}'.")
        return api_result
    except Exception as e:
        logger.error(f"Error en create_carrier: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al crear el transportista: {str(e)}"
        }

def update_carrier(tool_context, id: str, **kwargs):
    logger.info(f"TOOL EXECUTED: update_carrier(id='{id}', cambios={kwargs})")

    if not id:
        return {
            "status": "error",
            "message": "El ID del transportista es obligatorio.",
            "message_for_user": "Debes indicar el ID del transportista que deseas modificar."
        }

    # Filtrar los campos válidos para actualizar
    campos_validos = ["nombre", "codigo", "web", "telefono", "activo"]
    data = {k: v for k, v in kwargs.items() if k in campos_validos}

    if not data:
        return {
            "status": "error",
            "message": "No se proporcionaron campos válidos para actualizar.",
            "message_for_user": "Debes indicar al menos un campo válido para modificar."
        }

    # Convertir booleanos a enteros si es necesario
    if "activo" in data and isinstance(data["activo"], bool):
        data["activo"] = int(data["activo"])

    try:
        api_result = make_fs_request("PUT", f"/agenciatransportes/{id}", data=data)
        if api_result.get("status") == "success":
            api_result.setdefault("message_for_user", f"Transportista actualizado correctamente.")
        else:
            api_result.setdefault("message_for_user", f"No se pudo actualizar el transportista con ID '{id}'.")
        return api_result
    except Exception as e:
        logger.error(f"Error en update_carrier: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al actualizar el transportista: {str(e)}"
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

# --- GENERADOR DE REPORTES ---
def exportInventoryReport(tool_context, fecha_inicio: str, fecha_fin: str, 
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
    # upsert_product,
    update_product, # separacion de upsert: actualizar producto existente
    create_product, # separacion de upsert: crear producto nuevo
    delete_product,
    list_stock,
    adjust_stock,
    transfer_stock,
    stock_history,
    list_carriers,
    # upsert_carrier,
    update_carrier, # separacion de upsert: actualizar transportista existente
    create_carrier, # separacion de upsert: crear transportista nuevo
    delete_carrier,
    exportInventoryReport,
]


