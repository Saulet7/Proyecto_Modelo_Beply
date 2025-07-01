import requests
import os

requests_BASE_URL = "https://multiagente.beply.es/requests/3"

class APIClient:
    def __init__(self, base_url=requests_BASE_URL, token=None):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json"
        }
        # Si no se proporciona token, intentar obtenerlo de variable de entorno
        if not token:
            token = os.getenv('BEPLY_API_KEY')
        
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def set_token(self, token):
        """Configura el token de autenticación"""
        self.headers["Authorization"] = f"Bearer {token}"

    # --- CLIENTES ---

    def list_clientes(self):
        url = f"{self.base_url}/clientes"
        return requests.get(url, headers=self.headers).json()

    def create_cliente(self, data):
        url = f"{self.base_url}/clientes"
        return requests.post(url, json=data, headers=self.headers).json()

    def get_cliente(self, cliente_id):
        url = f"{self.base_url}/clientes/{cliente_id}"
        return requests.get(url, headers=self.headers).json()

    def update_cliente(self, cliente_id, data):
        url = f"{self.base_url}/clientes/{cliente_id}"
        return requests.put(url, json=data, headers=self.headers).json()

    def delete_cliente(self, cliente_id):
        url = f"{self.base_url}/clientes/{cliente_id}"
        return requests.delete(url, headers=self.headers).status_code

    # --- FACTURACLIENTES ---

    def list_facturaclientes(self):
        url = f"{self.base_url}/facturaclientes"
        return requests.get(url, headers=self.headers).json()

    def create_facturacliente(self, data):
        url = f"{self.base_url}/facturaclientes"
        return requests.post(url, json=data, headers=self.headers).json()

    def get_facturacliente(self, factura_id):
        url = f"{self.base_url}/facturaclientes/{factura_id}"
        return requests.get(url, headers=self.headers).json()

    def update_facturacliente(self, factura_id, data):
        url = f"{self.base_url}/facturaclientes/{factura_id}"
        return requests.put(url, json=data, headers=self.headers).json()

    def delete_facturacliente(self, factura_id):
        url = f"{self.base_url}/facturaclientes/{factura_id}"
        return requests.delete(url, headers=self.headers).status_code