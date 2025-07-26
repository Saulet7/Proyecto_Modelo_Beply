import logging
from typing import Optional, Any
from utils import make_fs_request

logger = logging.getLogger(__name__)

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

AGENT_TOOLS = [
    list_stock,
    adjust_stock,
    transfer_stock,
    stock_history
]
