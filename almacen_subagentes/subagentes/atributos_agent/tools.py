import logging
from typing import Optional, Any
from utils import make_fs_request

logger = logging.getLogger(__name__)

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
    

AGENT_TOOLS = [
    list_attributes,
    upsert_attribute,
    delete_attribute,
    assign_attribute_to_product
]