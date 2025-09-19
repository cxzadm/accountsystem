from beanie import Document
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class CompanyStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class Company(Document):
    name: str
    ruc: str
    legal_name: str
    address: str
    phone: str
    email: str
    status: CompanyStatus = CompanyStatus.ACTIVE
    fiscal_year_start: int = 1  # Mes de inicio del año fiscal
    currency: str = "USD"
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    created_by: str
    
    class Settings:
        name = "companies"
        indexes = [
            "ruc",
            "name",
            "status"
        ]

class CompanyCreate(BaseModel):
    name: str
    ruc: str
    legal_name: str
    address: str
    phone: str
    email: str
    fiscal_year_start: int = 1
    currency: str = "USD"

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    legal_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    status: Optional[CompanyStatus] = None
    fiscal_year_start: Optional[int] = None
    currency: Optional[str] = None

class CompanyResponse(BaseModel):
    id: str
    name: str
    ruc: str
    legal_name: str
    address: str
    phone: str
    email: str
    status: CompanyStatus
    fiscal_year_start: int
    currency: str
    created_at: datetime
    updated_at: datetime


