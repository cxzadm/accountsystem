from beanie import Document
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class LedgerEntryType(str, Enum):
    INITIAL = "initial"
    JOURNAL = "journal"
    ADJUSTMENT = "adjustment"
    CLOSING = "closing"

class LedgerEntry(Document):
    """Entrada en el mayor general"""
    account_id: str
    account_code: str
    account_name: str
    company_id: str
    entry_type: LedgerEntryType
    journal_entry_id: Optional[str] = None  # ID del asiento contable origen
    date: datetime
    description: str
    reference: Optional[str] = None
    debit_amount: float = 0.0
    credit_amount: float = 0.0
    running_debit_balance: float = 0.0  # Saldo acumulado débito
    running_credit_balance: float = 0.0  # Saldo acumulado crédito
    created_at: datetime = datetime.now()
    created_by: str
    
    class Settings:
        name = "ledger_entries"
        indexes = []

class LedgerEntryCreate(BaseModel):
    account_id: str
    account_code: str
    account_name: str
    entry_type: LedgerEntryType
    journal_entry_id: Optional[str] = None
    date: datetime
    description: str
    reference: Optional[str] = None
    debit_amount: float = 0.0
    credit_amount: float = 0.0

class LedgerEntryResponse(BaseModel):
    id: str
    account_id: str
    account_code: str
    account_name: str
    company_id: str
    entry_type: LedgerEntryType
    journal_entry_id: Optional[str]
    date: datetime
    description: str
    reference: Optional[str]
    debit_amount: float
    credit_amount: float
    running_debit_balance: float
    running_credit_balance: float
    created_at: datetime
    created_by: str

class AccountLedgerSummary(BaseModel):
    """Resumen de una cuenta en el mayor"""
    account_id: str
    account_code: str
    account_name: str
    account_type: str
    nature: str
    parent_code: Optional[str] = None
    level: int = 1
    initial_debit_balance: float
    initial_credit_balance: float
    current_debit_balance: float
    current_credit_balance: float
    net_balance: float
    total_debits: float
    total_credits: float
    entry_count: int
    last_transaction_date: Optional[datetime]
    entries: List[LedgerEntryResponse] = []









