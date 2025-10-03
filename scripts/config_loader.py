import json
import os
from pathlib import Path

def load_config():
    """Cargar configuración centralizada desde config.json"""
    # Obtener la ruta del archivo de configuración
    current_dir = Path(__file__).parent
    config_path = current_dir.parent / "config.json"
    
    # Leer el archivo de configuración
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Determinar el entorno (development por defecto)
    environment = os.getenv('ENVIRONMENT', 'development')
    env_config = config.get(environment, config['development'])
    
    return env_config

def get_backend_config():
    """Obtener configuración específica del backend"""
    config = load_config()
    return config['backend']

def get_database_config():
    """Obtener configuración específica de la base de datos"""
    config = load_config()
    return config['database']

def get_frontend_config():
    """Obtener configuración específica del frontend"""
    config = load_config()
    return config['frontend']

# Configuración por defecto
_config = load_config()
BACKEND_CONFIG = _config['backend']
DATABASE_CONFIG = _config['database']
FRONTEND_CONFIG = _config['frontend']


