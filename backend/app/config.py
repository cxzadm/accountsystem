from pydantic_settings import BaseSettings
from typing import List, ClassVar
import os
import sys
from pathlib import Path

# Agregar el directorio scripts al path para importar config_loader
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from config_loader import get_backend_config, get_database_config, get_frontend_config

# Obtener configuraciones fuera de la clase
database_config = get_database_config()
backend_config = get_backend_config()
frontend_config = get_frontend_config()

class Settings(BaseSettings):
    # Database - usar configuración centralizada
    mongodb_url: str = f"mongodb://{database_config['host']}:{database_config['port']}"
    database_name: str = "sistema_contable_ec"
    
    # Backend - usar configuración centralizada
    backend_port: int = backend_config['port']
    backend_host: str = backend_config['host']
    backend_ip: str = backend_config['ip']
    backend_protocol: str = backend_config['protocol']
    
    # Frontend - usar configuración centralizada
    frontend_port: int = frontend_config['port']
    
    # JWT
    secret_key: str = "tu-clave-secreta-super-segura-aqui"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # CORS - usar configuración centralizada del frontend
    allowed_origins: List[str] = [
        f"http://localhost:{frontend_config['port']}",
        f"http://{backend_config['ip']}:{frontend_config['port']}",
        f"{backend_config['protocol']}://{backend_config['ip']}:{frontend_config['port']}"
    ]
    
    # App
    app_name: str = "Sistema Contable  Accescont Ecuador"
    version: str = "1.0.0"
    debug: bool = True
    
    # SRI Configuration
    sri_ruc: str = ""
    sri_ambiente: str = "pruebas"  # pruebas, produccion
    
    class Config:
        env_file = ".env"

settings = Settings()











