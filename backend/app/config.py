from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "sistema_contable_ec"
    
    # JWT
    secret_key: str = "tu-clave-secreta-super-segura-aqui"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
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










