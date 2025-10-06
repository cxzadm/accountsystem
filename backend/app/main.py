from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import uvicorn
import sys
import os
from pathlib import Path

# Agregar el directorio raíz del proyecto al path para acceder a scripts
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Importar configuración centralizada
from scripts.config_loader import load_config, get_frontend_config, get_backend_config

from app.config import settings
from app.models.user import User
from app.models.company import Company
from app.models.account import Account
from app.models.journal import JournalEntry
from app.models.audit import AuditLog
from app.models.ledger import LedgerEntry
from app.models.document_type import DocumentType
from app.models.document_reservation import DocumentNumberReservation
from app.routes import auth, users, companies, accounts, journal, reports, sri, ledger
from app.routes import document_types
from app.routes import document_reservations
from app.routes import database

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    client = AsyncIOMotorClient(settings.mongodb_url)
    database = client[settings.database_name]
    
    await init_beanie(
        database=database,
        document_models=[
            User,
            Company,
            Account,
            JournalEntry,
            AuditLog,
            LedgerEntry,
            DocumentType,
            DocumentNumberReservation
        ],
        allow_index_dropping=True
    )
    
    yield
    
    # Shutdown
    client.close()

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Sistema contable multiempresa para Ecuador con cumplimiento SRI",
    lifespan=lifespan
)

# CORS - Configuración centralizada desde config.json
def get_cors_origins():
    """Obtener orígenes permitidos desde la configuración centralizada"""
    try:
        frontend_config = get_frontend_config()
        backend_config = get_backend_config()
        
        origins = ["*"]  # Permitir todos en desarrollo
        
        # Agregar localhost con puertos comunes
        for i in range(5173, 5180):  # Puertos comunes de desarrollo
            origins.extend([
                f"http://localhost:{i}",
                f"http://127.0.0.1:{i}"
            ])
        
        # Agregar rangos de IP comunes para desarrollo
        common_ips = ['192.168.68.113', '192.168.1.100', '192.168.0.100', '10.0.0.100']
        for ip in common_ips:
            for i in range(5173, 5180):
                origins.append(f"http://{ip}:{i}")
        
        # Agregar hosts permitidos desde la configuración
        if 'allowedHosts' in frontend_config:
            for host in frontend_config['allowedHosts']:
                # Agregar con diferentes puertos para desarrollo
                for port in [frontend_config['port'], 5173, 5174, 5175, 5176]:
                    origins.append(f"http://{host}:{port}")
                
                # También agregar el host sin puerto
                origins.append(f"http://{host}")
        
        # Agregar la IP del backend con diferentes puertos
        if 'ip' in backend_config:
            backend_ip = backend_config['ip']
            for port in [frontend_config['port'], 5173, 5174, 5175, 5176]:
                origins.append(f"http://{backend_ip}:{port}")
        
        return list(set(origins))  # Remover duplicados
        
    except Exception as e:
        print(f"⚠️ Error cargando configuración CORS: {e}")
        # Fallback a configuración por defecto
        return [
            "*",
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:5175",
            "http://localhost:5176",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
            "http://127.0.0.1:5175",
            "http://127.0.0.1:5176"
        ]

allowed_origins = get_cors_origins()
print(f"🌐 CORS Origins configurados: {len(allowed_origins)} orígenes")
print(f"   📋 Primeros orígenes: {allowed_origins[:5]}...")

# CORS permisivo para entornos de desarrollo y configuraciones dinámicas de puertos/IP
# Mantiene la lista calculada de orígenes y además permite cualquier origen vía regex.
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https?://.*",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Routes
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticación"])
app.include_router(users.router, prefix="/api/users", tags=["Usuarios"])
app.include_router(companies.router, prefix="/api/companies", tags=["Empresas"])
app.include_router(accounts.router, prefix="/api/accounts", tags=["Cuentas Contables"])
app.include_router(journal.router, prefix="/api/journal", tags=["Diario Contable"])
app.include_router(ledger.router, prefix="/api/ledger", tags=["Mayor General"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reportes"])
app.include_router(sri.router, prefix="/api/sri", tags=["Declaraciones SRI"])
app.include_router(document_types.router, prefix="/api", tags=["Tipos de Documentos"])
app.include_router(document_reservations.router, prefix="/api", tags=["Reservas de Documentos"])
app.include_router(database.router, prefix="/api/database", tags=["Base de Datos"])

@app.get("/")
async def root():
    return {
        "message": "Sistema Contable  Accescont Ecuador API",
        "version": settings.version,
        "status": "active"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.debug
    )
