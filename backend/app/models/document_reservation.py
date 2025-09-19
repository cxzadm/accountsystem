from beanie import Document
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReservationStatus(str):
    RESERVED = "reserved"
    USED = "used"
    CANCELLED = "cancelled"


class DocumentNumberReservation(Document):
    company_id: str
    document_type_id: str
    document_code: str
    sequence: int
    number: str  # e.g., CE-00001
    status: str = ReservationStatus.RESERVED
    journal_entry_id: Optional[str] = None
    reserved_by: Optional[str] = None
    reserved_at: datetime = datetime.now()
    used_at: Optional[datetime] = None

    class Settings:
        name = "document_reservations"
        indexes = [
            "company_id",
            "document_type_id",
            "number",
            "status",
            [("company_id", 1), ("number", 1), ("status", 1)]  # Unique constraint
        ]


class ReservationUpdate(BaseModel):
    status: Optional[str] = None
    number: Optional[str] = None
    sequence: Optional[int] = None
    journal_entry_id: Optional[str] = None

