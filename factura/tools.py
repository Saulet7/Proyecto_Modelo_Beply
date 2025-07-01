import logging
from api import APIClient

logger = logging.getLogger(__name__)

# Instancia global del cliente API
api_client = APIClient()

def list_facturaclientes(tool_context):
    """
    Lista todas las facturas de clientes disponibles en el sistema.
    """
    try:
        result = api_client.list_facturaclientes()
        return f"Facturas encontradas: {result}"
    except Exception as e:
        logger.error(f"Error al listar facturas: {e}")
        return f"Error al obtener la lista de facturas: {str(e)}"

def get_facturacliente(tool_context, factura_id: str):
    """
    Obtiene información detallada de una factura específica.
    
    Args:
        factura_id: ID de la factura a consultar
    """
    try:
        result = api_client.get_facturacliente(factura_id)
        return f"Información de la factura {factura_id}: {result}"
    except Exception as e:
        logger.error(f"Error al obtener factura {factura_id}: {e}")
        return f"Error al obtener información de la factura {factura_id}: {str(e)}"

def create_facturacliente(tool_context, data: dict):
    """
    Crea una nueva factura de cliente en el sistema.
    
    Args:
        data: Diccionario con los datos de la factura (cliente_id, monto, fecha, etc.)
    """
    try:
        result = api_client.create_facturacliente(data)
        return f"Factura creada exitosamente: {result}"
    except Exception as e:
        logger.error(f"Error al crear factura: {e}")
        return f"Error al crear la factura: {str(e)}"

def update_facturacliente(tool_context, factura_id: str, data: dict):
    """
    Actualiza la información de una factura existente.
    
    Args:
        factura_id: ID de la factura a actualizar
        data: Diccionario con los datos actualizados de la factura
    """
    try:
        result = api_client.update_facturacliente(factura_id, data)
        return f"Factura {factura_id} actualizada exitosamente: {result}"
    except Exception as e:
        logger.error(f"Error al actualizar factura {factura_id}: {e}")
        return f"Error al actualizar la factura {factura_id}: {str(e)}"

def delete_facturacliente(tool_context, factura_id: str):
    """
    Elimina una factura del sistema.
    
    Args:
        factura_id: ID de la factura a eliminar
    """
    try:
        status_code = api_client.delete_facturacliente(factura_id)
        if status_code == 200:
            return f"Factura {factura_id} eliminada exitosamente"
        else:
            return f"Error al eliminar factura {factura_id}. Código de estado: {status_code}"
    except Exception as e:
        logger.error(f"Error al eliminar factura {factura_id}: {e}")
        return f"Error al eliminar la factura {factura_id}: {str(e)}"

# Lista de herramientas disponibles para el agente
FACTURA_AGENT_TOOLS = [
    list_facturaclientes,
    get_facturacliente,
    create_facturacliente,
    update_facturacliente,
    delete_facturacliente
]
