from beanie import Document
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class AccountType(str, Enum):
    ACTIVO = "activo"
    PASIVO = "pasivo"
    PATRIMONIO = "patrimonio"
    INGRESOS = "ingresos"
    GASTOS = "gastos"
    COSTOS = "costos"

class AccountNature(str, Enum):
    DEUDORA = "deudora"
    ACREEDORA = "acreedora"

class Account(Document):
    code: str
    name: str
    description: Optional[str] = None
    account_type: AccountType
    nature: AccountNature
    parent_code: Optional[str] = None
    level: int = 1
    company_id: str
    is_active: bool = True
    is_editable: bool = True
    # Saldos de la cuenta
    initial_debit_balance: float = 0.0
    initial_credit_balance: float = 0.0
    current_debit_balance: float = 0.0
    current_credit_balance: float = 0.0
    # Fecha de último movimiento
    last_transaction_date: Optional[datetime] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    created_by: str
    
    class Settings:
        name = "accounts"
        indexes = [
            "code",
            "company_id",
            "account_type",
            "is_active"
        ]

class AccountCreate(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    account_type: AccountType
    nature: AccountNature
    parent_code: Optional[str] = None
    level: int = 1
    is_editable: bool = True
    initial_debit_balance: float = 0.0
    initial_credit_balance: float = 0.0

class AccountUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    is_editable: Optional[bool] = None

class AccountResponse(BaseModel):
    id: str
    code: str
    name: str
    description: Optional[str]
    account_type: AccountType
    nature: AccountNature
    parent_code: Optional[str]
    level: int
    company_id: str
    is_active: bool
    is_editable: bool
    initial_debit_balance: float
    initial_credit_balance: float
    current_debit_balance: float
    current_credit_balance: float
    last_transaction_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class AccountBalance(BaseModel):
    account: AccountResponse
    debit_balance: float = 0.0
    credit_balance: float = 0.0
    net_balance: float = 0.0

class InitialBalanceUpdate(BaseModel):
    account_code: str
    initial_debit_balance: float = 0.0
    initial_credit_balance: float = 0.0
    name: Optional[str] = None
    account_type: Optional[AccountType] = None
    nature: Optional[AccountNature] = None
    description: Optional[str] = None
    level: Optional[int] = 1
    parent_code: Optional[str] = None
    is_editable: Optional[bool] = True

class InitialBalancesBatch(BaseModel):
    balances: List[InitialBalanceUpdate]

class ChartOfAccountsExport(BaseModel):
    code: str
    name: str
    account_type: str
    nature: str
    initial_debit_balance: float = 0.0
    initial_credit_balance: float = 0.0

