from beanie import Document
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class JournalEntryStatus(str, Enum):
    DRAFT = "draft"
    POSTED = "posted"
    REVERSED = "reversed"

class JournalEntryType(str, Enum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    ADJUSTMENT = "adjustment"
    CLOSING = "closing"

class JournalLine(BaseModel):
    account_code: str
    account_name: str
    description: str
    debit: float = 0.0
    credit: float = 0.0
    reference: Optional[str] = None

class JournalEntry(Document):
    entry_number: str
    date: datetime
    description: str
    entry_type: JournalEntryType = JournalEntryType.MANUAL
    status: JournalEntryStatus = JournalEntryStatus.DRAFT
    document_type_id: Optional[str] = None
    document_type_code: Optional[str] = None
    lines: List[JournalLine]
    total_debit: float = 0.0
    total_credit: float = 0.0
    company_id: str
    created_by: str
    responsable: Optional[str] = None  # Nombre del usuario responsable
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    
    class Settings:
        name = "journal_entries"
        indexes = []

class JournalEntryCreate(BaseModel):
    entry_number: str
    date: datetime
    description: str
    entry_type: JournalEntryType = JournalEntryType.MANUAL
    document_type_id: Optional[str] = None
    document_type_code: Optional[str] = None
    lines: List[JournalLine]
    responsable: Optional[str] = None

class JournalEntryUpdate(BaseModel):
    date: Optional[datetime] = None
    description: Optional[str] = None
    entry_type: Optional[JournalEntryType] = None
    document_type_id: Optional[str] = None
    document_type_code: Optional[str] = None
    lines: Optional[List[JournalLine]] = None
    responsable: Optional[str] = None

class JournalEntryResponse(BaseModel):
    id: str
    entry_number: str
    document_type_id: Optional[str]
    document_type_code: Optional[str]
    date: datetime
    description: str
    entry_type: JournalEntryType
    status: JournalEntryStatus
    lines: List[JournalLine]
    total_debit: float
    total_credit: float
    company_id: str
    created_by: str
    responsable: Optional[str]
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class JournalEntryApprove(BaseModel):
    approved: bool
    notes: Optional[str] = None






