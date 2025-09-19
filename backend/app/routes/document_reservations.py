from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from app.models.user import User
from app.auth.dependencies import require_permission
from app.models.document_reservation import DocumentNumberReservation, ReservationUpdate

router = APIRouter(prefix="/document-reservations", tags=["Document Reservations"])


@router.get("/", response_model=List[dict])
async def list_reservations(
    company_id: str = Query(...),
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_permission("companies:update"))
):
    query = {"company_id": company_id}
    if status:
        query["status"] = status
    items = await DocumentNumberReservation.find(query).sort("-reserved_at").to_list()
    return [
        {
            "id": str(i.id),
            "company_id": i.company_id,
            "document_type_id": i.document_type_id,
            "document_code": i.document_code,
            "sequence": i.sequence,
            "number": i.number,
            "status": i.status,
            "journal_entry_id": i.journal_entry_id,
            "reserved_by": i.reserved_by,
            "reserved_at": i.reserved_at,
            "used_at": i.used_at
        }
        for i in items
    ]


@router.put("/{reservation_id}", response_model=dict)
async def update_reservation(
    reservation_id: str,
    data: ReservationUpdate,
    current_user: User = Depends(require_permission("companies:update"))
):
    res = await DocumentNumberReservation.get(reservation_id)
    if not res:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    # Solo permitir cancelar (no permitir cambiar a used manualmente, lo hace el sistema al crear asiento)
    payload = data.dict(exclude_unset=True)
    if "status" in payload and payload["status"] not in ("reserved", "cancelled"):
        raise HTTPException(status_code=400, detail="Estado no permitido")
    for k, v in payload.items():
        setattr(res, k, v)
    await res.save()
    return {"message": "Reserva actualizada"}


