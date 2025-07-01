"""Utilidades comunes para el servicio ADK de ChatAI."""

import logging
import requests
from typing import Optional, Dict, Any
from urllib.parse import urljoin
import os

from config import configs

logger = logging.getLogger(__name__)

def make_fs_request(method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None,
                    api_url: Optional[str] = None, api_token: Optional[str] = None, 
                    session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Realiza llamadas a la API de FacturaScripts.
    
    Args:
        method: Método HTTP ("GET", "POST", "PUT", "DELETE", etc.)
        endpoint: Ruta del endpoint, con o sin "/" inicial.
        params: Parámetros para la URL query (opcional).
        data: Datos para el cuerpo de la petición (opcional).
        api_url: URL base de la API (opcional).
        api_token: Token de autenticación de la API (opcional).
        session_id: ID de la sesión para buscar credenciales específicas (opcional).
    
    Returns:
        Dict con status "success"/"error" y datos o mensaje de error.
    """
    # Prioridad: 
    # 1. Parámetros de función explícitos
    # 2. Credenciales específicas de sesión (si se proporciona session_id)
    # 3. Configuración global
    
    # Intentar obtener credenciales específicas de sesión
    # Si no se proporcionó un session_id explícito, intentar obtenerlo de la variable de entorno
    if not session_id:
        session_id = os.environ.get("CURRENT_SESSION_ID")
        if session_id:
            logger.debug(f"Usando session_id de variable de entorno: {session_id}")
    
    if session_id:
        session_api_url = os.environ.get(f"FS_API_URL_{session_id}")
        session_api_token = os.environ.get(f"FS_API_TOKEN_{session_id}")
        
        if session_api_url and session_api_token:
            logger.debug(f"Usando credenciales específicas para la sesión {session_id}")
            fs_api_url = api_url or session_api_url
            fs_api_token = api_token or session_api_token
        else:
            logger.debug(f"No se encontraron credenciales específicas para la sesión {session_id}, usando configuración global")
            fs_api_url = api_url or (configs.fs_api_url if configs else None)
            fs_api_token = api_token or (configs.fs_api_token if configs else None)
    else:
        # Usar configuración global si no hay session_id
        fs_api_url = api_url or (configs.fs_api_url if configs else None)
        fs_api_token = api_token or (configs.fs_api_token if configs else None)
    
    if not fs_api_url or not fs_api_token:
        logger.error("API URL o Token no configurados.")
        return {
            "status": "error", 
            "message": "Error de configuración: URL o Token de API no encontrados.",
            "message_for_user": "No puedo conectarme a la API de Beply. Por favor, verifica tu configuración."
        }
    
    # Asegurar que la URL base tenga el prefijo /api/3
    if not fs_api_url.endswith('/api/3') and not fs_api_url.endswith('/api/3/'):
        # Si no termina con /api/3, verificar si contiene /api/3 en alguna parte
        if '/api/3/' not in fs_api_url and '/api/3' not in fs_api_url:
            # No contiene /api/3, así que lo añadimos
            fs_api_url = f"{fs_api_url.rstrip('/')}/api/3"
            logger.info(f"📌 URL CORREGIDA: Añadido /api/3 a la URL base: {fs_api_url}")
    
    headers = {"token": fs_api_token}
    full_url = urljoin(fs_api_url + "/", endpoint.lstrip('/'))

    # LOG DETALLADO DE LA PETICIÓN
    logger.info(f"🔍 PETICIÓN API: {method} {full_url}")
    logger.info(f"🔑 HEADERS: token='{fs_api_token[:5]}...'")
    if params:
        logger.info(f"📝 PARAMS: {params}")
    if data:
        logger.info(f"📄 BODY: {data}")

    request_kwargs = {"headers": headers, "timeout": 15}
    http_method = method.upper()

    if http_method in ["POST", "PUT", "PATCH"]:
        request_kwargs["data"] = data
        if params:
            request_kwargs["params"] = params
    else:  # GET, DELETE, HEAD, OPTIONS...
        request_kwargs["params"] = params
        if data:
            request_kwargs["data"] = data
            logger.warning(f"Enviando 'data' con método {http_method}, se usará como form-data.")

    try:
        response = requests.request(method, full_url, **request_kwargs)
        
        # LOG DETALLADO DE LA RESPUESTA
        logger.info(f"📊 RESPUESTA: Status {response.status_code}")
        try:
            # Mostrar la respuesta completa, sin truncar
            content_full = response.content.decode('utf-8', errors='replace')
            logger.info(f"📄 CONTENIDO COMPLETO: {content_full}")
        except Exception as e:
            logger.info(f"📄 CONTENIDO: No se pudo decodificar")
            
        response.raise_for_status()

        if response.status_code == 204:  # No Content
            return {"status": "success", "message": "Operación exitosa (No Content)."}
        try:
            json_response = response.json()
            # Para endpoint /empresas que devuelve lista
            if endpoint == "/empresas" and isinstance(json_response, list) and json_response:
                return {"status": "success", "data": json_response[0]}
            elif endpoint == "/empresas" and isinstance(json_response, list):
                return {"status": "not_found", "message": "No se encontraron empresas."}
            else:
                return {"status": "success", "data": json_response}
        except requests.exceptions.JSONDecodeError:
            logger.warning(f"Respuesta no JSON. Estado: {response.status_code}")
            if 200 <= response.status_code < 300:
                return {"status": "success", "message": f"Operación exitosa (código {response.status_code}) sin cuerpo JSON."}
            else:
                return {"status": "error", "message": f"Error API: Respuesta no JSON.", "raw_response": response.text[:200]}

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"Error HTTP: {http_err.response.status_code}", exc_info=False)
        error_detail = f"Error HTTP {http_err.response.status_code}"
        try:
            error_json = http_err.response.json()
            error_detail += f": {error_json.get('message', error_json.get('error', http_err.response.text[:50]))}"
        except requests.exceptions.JSONDecodeError:
            error_detail += f": {http_err.response.text[:50]}"
        return {"status": "error", "message": error_detail}
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Error de solicitud: {req_err}", exc_info=False)
        return {"status": "error", "message": f"Error de conexión: {req_err}"}
    except Exception as e:
        logger.error(f"Error inesperado: {e}", exc_info=True)
        return {"status": "error", "message": f"Error inesperado: {e}"}

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
