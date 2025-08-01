import logging
from typing import Optional, Any
from utils import make_fs_request

logger = logging.getLogger(__name__)

def list_attributes(tool_context, **filters):
    logger.info(f"TOOL EXECUTED: list_attributes(filters={filters})")

    try:
        codproducto = filters.pop("codproducto", None)
        idproducto = filters.pop("idproducto", None)
        valor = filters.pop("valor", None)

        # 1. Obtener atributos
        atributos_result = make_fs_request("GET", "/atributos", params=filters)
        if atributos_result.get("status") != "success":
            return {
                "status": "error",
                "message": "No se pudo obtener la lista de atributos.",
                "message_for_user": "No se pudo obtener la lista de atributos."
            }
        atributos = atributos_result.get("data", [])

        # 2. Obtener todos los atributovalores
        valores_result = make_fs_request("GET", "/atributovalores")
        if valores_result.get("status") != "success":
            return {
                "status": "error",
                "message": "No se pudieron obtener los valores de atributos.",
                "message_for_user": "No se pudieron obtener los valores de atributos."
            }
        atributovalores = valores_result.get("data", [])
        valores_por_id = {v["id"]: v for v in atributovalores}

        # 3. Obtener variantes del producto
        variantes_params = {}
        if codproducto or idproducto:
            productos_result = make_fs_request("GET", "/productos", params={"codproducto": codproducto, "idproducto": idproducto})
            if productos_result.get("status") != "success" or not productos_result.get("data"):
                return {
                    "status": "error",
                    "message": "No se encontró el producto.",
                    "message_for_user": "No se encontró el producto."
                }
            idproducto = productos_result["data"][0]["idproducto"]
            variantes_params["idproducto"] = idproducto

        variantes_result = make_fs_request("GET", "/variantes", params=variantes_params)
        if variantes_result.get("status") != "success":
            return {
                "status": "error",
                "message": "No se pudieron obtener las variantes.",
                "message_for_user": "No se pudieron obtener las variantes del producto."
            }
        variantes = variantes_result.get("data", [])

        # 4. Relacionar atributos con variantes
        from collections import defaultdict
        asignaciones_por_atributo = defaultdict(list)
        for variante in variantes:
            for i in range(1, 5):
                valor_id = variante.get(f"idatributovalor{i}")
                if not valor_id:
                    continue
                valor_info = valores_por_id.get(valor_id)
                if not valor_info:
                    continue
                if valor and valor_info.get("valor") != valor:
                    continue  # filtrar por valor si se especificó

                codatributo = valor_info.get("codatributo")
                asignaciones_por_atributo[codatributo].append({
                    "idvariante": variante.get("idvariante"),
                    "idproducto": variante.get("idproducto"),
                    "valor": valor_info.get("valor"),
                    "idatributovalor": valor_id
                })

        # 5. Enriquecer atributos
        atributos_enriquecidos = []
        for atributo in atributos:
            codatributo = atributo.get("codatributo")
            asignaciones = asignaciones_por_atributo.get(codatributo, [])
            atributo_copia = atributo.copy()
            atributo_copia["asignaciones"] = asignaciones
            if valor or codproducto or idproducto:
                if asignaciones:
                    atributos_enriquecidos.append(atributo_copia)
            else:
                atributos_enriquecidos.append(atributo_copia)

        mensaje_usuario = f"Se encontraron {len(atributos_enriquecidos)} atributos"
        if codproducto:
            mensaje_usuario += f" asignados al producto '{codproducto}'"
        elif valor:
            mensaje_usuario += f" con valor '{valor}'"
        mensaje_usuario += "."

        return {
            "status": "success",
            "data": atributos_enriquecidos,
            "message": "Atributos procesados correctamente.",
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

def assign_attribute_to_product(tool_context, idvariante: int, codatributo: str, valor: str):
    logger.info(f"TOOL EXECUTED: assign_attribute_to_product(idvariante={idvariante}, codatributo='{codatributo}', valor='{valor}')")

    try:
        # 1. Buscar el atributovalor que corresponde al codatributo y valor
        valores_result = make_fs_request("GET", "/atributovalores")
        if valores_result.get("status") != "success":
            return {
                "status": "error",
                "message": "No se pudieron obtener los valores de atributos.",
                "message_for_user": "No se pudo encontrar el valor del atributo a asignar."
            }
        atributovalores = valores_result.get("data", [])
        valor_encontrado = next((v for v in atributovalores if v["codatributo"] == codatributo and v["valor"] == valor), None)
        if not valor_encontrado:
            return {
                "status": "error",
                "message": "Valor de atributo no encontrado.",
                "message_for_user": "No se encontró el valor indicado para ese atributo."
            }
        idatributovalor = valor_encontrado["id"]

        # 2. Obtener la variante a modificar
        variante_result = make_fs_request("GET", f"/variantes/{idvariante}")
        if variante_result.get("status") != "success":
            return {
                "status": "error",
                "message": "No se pudo obtener la variante.",
                "message_for_user": "No se encontró la variante indicada."
            }
        variante = variante_result["data"]

        # 3. Asignar al primer campo libre entre idatributovalor1..4
        for i in range(1, 5):
            campo = f"idatributovalor{i}"
            if not variante.get(campo):
                variante[campo] = idatributovalor
                break
            # Si ya está asignado ese codatributo, reemplazar
            elif valores_result["data"]:
                val = valores_result["data"]
                idval_existente = variante.get(campo)
                if idval_existente:
                    cod_existente = next((v["codatributo"] for v in val if v["id"] == idval_existente), None)
                    if cod_existente == codatributo:
                        variante[campo] = idatributovalor
                        break
        else:
            return {
                "status": "error",
                "message": "No hay campo libre para asignar el atributo.",
                "message_for_user": "No se puede asignar más atributos a esta variante (máximo 4)."
            }

        # 4. Actualizar la variante
        update_result = make_fs_request("PUT", f"/variantes/{idvariante}", data=variante)
        if update_result.get("status") == "success":
            update_result.setdefault("message_for_user", f"Atributo '{codatributo}' asignado a la variante correctamente.")
        else:
            update_result.setdefault("message_for_user", "No se pudo asignar el atributo a la variante.")

        return update_result

    except Exception as e:
        logger.error(f"Error en assign_attribute_to_product: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "message_for_user": f"Ocurrió un error al asignar el atributo a la variante: {str(e)}"
        }

AGENT_TOOLS = [
    list_attributes,
    upsert_attribute,
    delete_attribute,
    assign_attribute_to_product
]