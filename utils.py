"""Utilidades comunes para el servicio ADK de ChatAI."""

import logging
import requests
from typing import Optional, Dict, Any
from urllib.parse import urljoin
import os

from config import configs

logger = logging.getLogger(__name__)

def make_fs_request(method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
    """
    Realiza una petición a la API de FacturaScripts usando la configuración global.
    
    Args:
        method: Método HTTP (GET, POST, PUT, DELETE)
        endpoint: Endpoint de la API (ej: "/clientes")
        data: Datos a enviar (se envían como form-data para POST/PUT)
        params: Parámetros de consulta para GET
        
    Returns:
        Dict con la respuesta estructurada
    """
    url = f"{configs.fs_api_url}{endpoint}"
    
    # Headers corregidos - usar Token en lugar de Authorization
    headers = {
        "Token": configs.fs_api_token,  # Cambiado: Token directo sin Bearer
        "Accept": "application/json"
    }
    
    # Solo agregar Content-Type para métodos que envían datos
    if method in ["POST", "PUT"] and data:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    
    logger.info(f"FS API Request: {method} {url}")
    logger.debug(f"Headers: {headers}")
    logger.debug(f"Data: {data}")
    logger.debug(f"Params: {params}")
    
    try:
        # Hacer la petición usando requests estándar
        import requests
        
        if method == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=30)
        elif method == "POST":
            response = requests.post(url, headers=headers, data=data, timeout=30)
        elif method == "PUT":
            response = requests.put(url, headers=headers, data=data, timeout=30)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=30)
        else:
            raise ValueError(f"Método HTTP no soportado: {method}")
        
        logger.info(f"FS API Response: {response.status_code}")
        logger.debug(f"Response headers: {dict(response.headers)}")
        logger.debug(f"Response text: {response.text[:500]}...")
        
        # Procesar respuesta
        if response.status_code in [200, 201]:
            try:
                response_data = response.json()
                return {
                    "status": "success",
                    "data": response_data,
                    "message": "Operación completada exitosamente"
                }
            except ValueError:
                # Si no es JSON válido pero el status es exitoso
                return {
                    "status": "success",
                    "data": response.text,
                    "message": "Operación completada exitosamente (respuesta no JSON)"
                }
        else:
            # Error de API
            try:
                error_data = response.json()
                error_message = error_data.get('message', error_data.get('error', 'Error desconocido'))
            except ValueError:
                error_message = response.text or f'Error HTTP {response.status_code}'
            
            return {
                "status": "error",
                "message": f"Error {response.status_code}: {error_message}",
                "status_code": response.status_code
            }
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error de petición FS API: {e}")
        return {
            "status": "error",
            "message": f"Error de conexión: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Error inesperado en FS API: {e}")
        return {
            "status": "error",
            "message": f"Error inesperado: {str(e)}"
        }

def make_fs_request_with_retry(method: str, endpoint: str, params: Optional[Dict] = None, 
                      data: Optional[Dict] = None, api_url: Optional[str] = None, 
                      api_token: Optional[str] = None, session_id: Optional[str] = None,
                      max_retries: int = 2) -> Dict[str, Any]:
    """
    Realiza llamadas a la API de FacturaScripts con reintentos.
    
    Si la primera llamada falla, intenta nuevamente con credenciales globales
    como último recurso.
    
    Args:
        method, endpoint, params, data, api_url, api_token, session_id: Igual que make_fs_request
        max_retries: Número máximo de intentos (por defecto: 2)
    
    Returns:
        Dict con status "success"/"error" y datos o mensaje de error.
    """
    result = make_fs_request(method, endpoint, params, data, api_url, api_token, session_id)
    
    # Si la respuesta fue exitosa o no es un error de autenticación (401), devuelve el resultado directamente
    if result.get("status") == "success" or "401" not in result.get("message", ""):
        return result
    
    # Si hay un error 401 (Unauthorized), intenta nuevamente con credenciales globales
    retry_count = 0
    while retry_count < max_retries and result.get("status") == "error" and "401" in result.get("message", ""):
        retry_count += 1
        logger.warning(f"Reintento {retry_count}/{max_retries}: Error de autenticación, intentando con credenciales globales")
        
        # En el primer reintento, usar credenciales globales explícitamente
        if retry_count == 1 and configs:
            result = make_fs_request(method, endpoint, params, data, 
                                     configs.fs_api_url, configs.fs_api_token)
        # En el segundo reintento, intentar con credenciales de entorno
        elif retry_count == 2:
            env_url = os.getenv("FACTURASCRIPTS_API_URL")
            env_token = os.getenv("FACTURASCRIPTS_API_TOKEN")
            if env_url and env_token:
                result = make_fs_request(method, endpoint, params, data, env_url, env_token)
        
    # Si después de los reintentos seguimos con error, añadir un mensaje más amigable
    if result.get("status") == "error" and "message_for_user" not in result:
        result["message_for_user"] = "Hubo un problema al conectar con el sistema de Beply. Por favor, verifica tu conexión y credenciales."
    
    return result

def fetch_company_context() -> Optional[Dict[str, Any]]:
    """Obtiene la información de la primera empresa desde la API."""
    # El session_id se obtendrá automáticamente dentro de make_fs_request
    logger.info(f"Obteniendo información de empresa...")
    result = make_fs_request("GET", "/empresas", params={"limit": 1})
    if result.get("status") == "success" and isinstance(result.get("data"), dict):
        return result["data"]
    else:
        error_message = result.get("message", "Error desconocido")
        logger.error(f"Error al obtener información de empresa: {error_message}")
        return None

def format_company_context(company_data: Optional[Dict[str, Any]]) -> str:
    """Formatea los datos de la empresa para el contexto."""
    if not company_data:
        return "Información de la empresa no disponible."
    name = company_data.get('nombre', 'N/A')
    cif = company_data.get('cifnif', 'N/A')
    email = company_data.get('email', 'N/A')
    context_str = (
        f"- Nombre: {name}\n"
        f"- CIF/NIF: {cif}\n"
        f"- Email: {email}"
    )
    return context_str
