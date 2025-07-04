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

    # --- CLIENTES ---

    def list_clientes(self):
        url = f"{self.base_url}/clientes"
        return requests.get(url, headers=self.headers).json()

    def create_cliente(self, data):
        url = f"{self.base_url}/clientes"
        # Usar data en lugar de json para form-data
        return requests.post(url, data=data, headers=self.headers).json()

    def get_cliente(self, cliente_id):
        url = f"{self.base_url}/clientes/{cliente_id}"
        return requests.get(url, headers=self.headers).json()

    def update_cliente(self, cliente_id, data):
        url = f"{self.base_url}/clientes/{cliente_id}"
        # Usar data en lugar de json para form-data
        return requests.put(url, data=data, headers=self.headers).json()

    def delete_cliente(self, cliente_id):
        url = f"{self.base_url}/clientes/{cliente_id}"
        return requests.delete(url, headers=self.headers).status_code

    # --- FACTURACLIENTES ---

    def list_facturaclientes(self):
        url = f"{self.base_url}/facturaclientes"
        return requests.get(url, headers=self.headers).json()

    def create_facturacliente(self, data):
        url = f"{self.base_url}/facturaclientes"
        # Usar data en lugar de json para form-data
        return requests.post(url, data=data, headers=self.headers).json()

    def get_facturacliente(self, factura_id):
        url = f"{self.base_url}/facturaclientes/{factura_id}"
        return requests.get(url, headers=self.headers).json()

    def update_facturacliente(self, factura_id, data):
        url = f"{self.base_url}/facturaclientes/{factura_id}"
        # Usar data en lugar de json para form-data
        return requests.put(url, data=data, headers=self.headers).json()

    def delete_facturacliente(self, factura_id):
        url = f"{self.base_url}/facturaclientes/{factura_id}"
        return requests.delete(url, headers=self.headers).status_code