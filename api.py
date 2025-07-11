import requests
import os

API_BASE_URL = "https://multiagente.beply.es/api/3"  # Corregido: api en lugar de requests

class APIClient:
    def __init__(self, base_url=API_BASE_URL, token=None):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded",  # Cambiado para form-data
            "Accept": "application/json"
        }
        # Si no se proporciona token, intentar obtenerlo de variable de entorno
        if not token:
            token = os.getenv('BEPLY_API_KEY')
        
        if token:
            self.headers["Token"] = token  # Cambiado: Token directo sin Bearer

    def set_token(self, token):
        """Configura el token de autenticación"""
        self.headers["Token"] = token  # Cambiado: Token directo sin Bearer