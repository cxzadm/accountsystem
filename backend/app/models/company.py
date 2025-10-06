from beanie import Document
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Any
from datetime import datetime
from enum import Enum
from bson import ObjectId

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
    created_by: str = Field(..., description="ID del usuario que creó la empresa")
    
    @model_validator(mode='before')
    @classmethod
    def validate_before(cls, values: Any) -> Any:
        """Convierte ObjectId a string antes de la validación"""
        if isinstance(values, dict) and 'created_by' in values:
            if isinstance(values['created_by'], ObjectId):
                values['created_by'] = str(values['created_by'])
        return values
    
    class Settings:
        name = "companies"
        indexes = []

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


