"""Configuración para el proyecto BEPLY."""

import os
from typing import Optional

class Config:
    """Clase de configuración para variables del proyecto."""
    
    def __init__(self):
        # API de FacturaScripts/BEPLY
        self.fs_api_url: Optional[str] = os.getenv('BEPLY_API_URL', 'https://multiagente.beply.es/api/3')
        self.fs_api_token: Optional[str] = os.getenv('BEPLY_API_KEY')
        
        # Configuración de logging
        self.log_level: str = os.getenv('LOG_LEVEL', 'INFO')
        
        # Otras configuraciones
        self.debug_mode: bool = os.getenv('DEBUG_MODE', 'False').lower() == 'true'

# Instancia global de configuración
configs = Config()
