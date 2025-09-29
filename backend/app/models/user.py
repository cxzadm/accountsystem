from beanie import Document
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    CONTADOR = "contador"
    AUDITOR = "auditor"
    INTERNO = "interno"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class AuditEntry(BaseModel):
    action: str
    timestamp: datetime
    ip_address: str
    user_agent: str
    details: Optional[dict] = None

class User(Document):
    username: str
    email: EmailStr
    password_hash: str
    first_name: str
    last_name: str
    role: UserRole
    status: UserStatus = UserStatus.ACTIVE
    permissions: List[str] = []
    companies: List[str] = []  # IDs de empresas
    last_login: Optional[datetime] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    created_by: Optional[str] = None
    audit_log: List[AuditEntry] = []
    
    class Settings:
        name = "users"
        indexes = []

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: UserRole
    status: UserStatus = UserStatus.ACTIVE
    companies: List[str] = []

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    permissions: Optional[List[str]] = None
    companies: Optional[List[str]] = None

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    first_name: str
    last_name: str
    role: UserRole
    status: UserStatus
    permissions: List[str]
    companies: List[str]
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

