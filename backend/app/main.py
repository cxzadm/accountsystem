from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import uvicorn

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

# CORS (permitir todos los orígenes en desarrollo; usamos Bearer tokens, no cookies)
# CORS
# En desarrollo: permitir Vite dev server y mismo host explícitamente (mitiga proxies intermedios que quitan headers)
allowed_origins = [
    "*",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
