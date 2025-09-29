from beanie import Document
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DocumentType(Document):
    code: str                # CE, CI, 01, 21, etc.
    name: str                # COMPROBANTE DE EGRESO, FACTURA DE VENTA, etc.
    control_number: Optional[str] = None  # último número asignado formateado, opcional
    establishment_point: Optional[str] = None  # 001-001
    receipt_type: Optional[str] = None    # catálogo SRI si aplica (ej. "7")
    bank_movement: Optional[str] = None   # D/C
    customer_movement: Optional[str] = None  # D/C
    supplier_movement: Optional[str] = None  # D/C
    product_movement: Optional[str] = None   # I/E
    is_electronic: bool = False
    responsible_code: Optional[str] = None   # BFC
    responsible_name: Optional[str] = None   # BRYAM CABRERA

    # Secuencia
    next_sequence: int = 0
    padding: int = 5  # CE-00001

    company_id: str
    is_active: bool = True

    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    created_by: Optional[str] = None

    class Settings:
        name = "document_types"
        indexes = []


class DocumentTypeCreate(BaseModel):
    code: str
    name: str
    establishment_point: Optional[str] = None
    receipt_type: Optional[str] = None
    bank_movement: Optional[str] = None
    customer_movement: Optional[str] = None
    supplier_movement: Optional[str] = None
    product_movement: Optional[str] = None
    is_electronic: bool = False
    responsible_code: Optional[str] = None
    responsible_name: Optional[str] = None
    padding: int = 5


class DocumentTypeUpdate(BaseModel):
    name: Optional[str] = None
    establishment_point: Optional[str] = None
    receipt_type: Optional[str] = None
    bank_movement: Optional[str] = None
    customer_movement: Optional[str] = None
    supplier_movement: Optional[str] = None
    product_movement: Optional[str] = None
    is_electronic: Optional[bool] = None
    responsible_code: Optional[str] = None
    responsible_name: Optional[str] = None
    padding: Optional[int] = None
    is_active: Optional[bool] = None


class DocumentTypeResponse(BaseModel):
    id: str
    code: str
    name: str
    control_number: Optional[str]
    establishment_point: Optional[str]
    receipt_type: Optional[str]
    bank_movement: Optional[str]
    customer_movement: Optional[str]
    supplier_movement: Optional[str]
    product_movement: Optional[str]
    is_electronic: bool
    responsible_code: Optional[str]
    responsible_name: Optional[str]
    next_sequence: int
    padding: int
    company_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

