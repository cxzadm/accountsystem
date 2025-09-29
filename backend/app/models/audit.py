from beanie import Document
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class AuditAction(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    APPROVE = "approve"
    REJECT = "reject"
    EXPORT = "export"
    IMPORT = "import"

class AuditModule(str, Enum):
    AUTH = "auth"
    USERS = "users"
    COMPANIES = "companies"
    ACCOUNTS = "accounts"
    JOURNAL = "journal"
    REPORTS = "reports"
    SRI = "sri"
    ASSETS = "assets"
    PAYABLES = "payables"
    RECEIVABLES = "receivables"

class AuditLog(Document):
    user_id: str
    username: str
    action: AuditAction
    module: AuditModule
    resource_id: Optional[str] = None
    resource_type: Optional[str] = None
    description: str
    ip_address: str
    user_agent: str
    company_id: Optional[str] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now()
    
    class Settings:
        name = "audit_logs"
        indexes = []

class AuditLogResponse(BaseModel):
    id: str
    user_id: str
    username: str
    action: AuditAction
    module: AuditModule
    resource_id: Optional[str]
    resource_type: Optional[str]
    description: str
    ip_address: str
    user_agent: str
    company_id: Optional[str]
    old_values: Optional[Dict[str, Any]]
    new_values: Optional[Dict[str, Any]]
    timestamp: datetime







