from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from typing import List, Optional
from app.models.journal import JournalEntry, JournalEntryCreate, JournalEntryUpdate, JournalEntryResponse, JournalEntryApprove, JournalLine
from app.models.document_reservation import DocumentNumberReservation, ReservationStatus
from app.models.user import User
from app.auth.dependencies import get_current_user, require_permission, log_audit, AuditAction, AuditModule
from app.services.ledger_service import LedgerService
from datetime import datetime
from bson import ObjectId

router = APIRouter()

@router.get("/", response_model=List[JournalEntryResponse])
async def get_journal_entries(
    company_id: str = Query(..., description="ID de la empresa"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[str] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Fecha fin (YYYY-MM-DD)"),
    status: Optional[str] = Query(None),
    entry_type: Optional[str] = Query(None),
    current_user: User = Depends(require_permission("journal:read"))
):
    """Obtener lista de asientos contables con filtros"""
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta empresa"
        )
    
    query = {"company_id": company_id}
    
    if start_date:
        query["date"] = {"$gte": datetime.fromisoformat(start_date)}
    
    if end_date:
        if "date" in query:
            query["date"]["$lte"] = datetime.fromisoformat(end_date)
        else:
            query["date"] = {"$lte": datetime.fromisoformat(end_date)}
    
    if status:
        query["status"] = status
    
    if entry_type:
        query["entry_type"] = entry_type
    
    entries = await JournalEntry.find(query).skip(skip).limit(limit).to_list()
    
    return [
        JournalEntryResponse(
            id=str(entry.id),
            entry_number=entry.entry_number,
            document_type_id=getattr(entry, "document_type_id", None),
            document_type_code=getattr(entry, "document_type_code", None),
            date=entry.date,
            description=entry.description,
            entry_type=entry.entry_type,
            status=entry.status,
            lines=entry.lines,
            total_debit=entry.total_debit,
            total_credit=entry.total_credit,
            company_id=entry.company_id,
            created_by=entry.created_by,
            approved_by=entry.approved_by,
            approved_at=entry.approved_at,
            created_at=entry.created_at,
            updated_at=entry.updated_at
        )
        for entry in entries
    ]

@router.get("/{entry_id}/", response_model=JournalEntryResponse)
async def get_journal_entry(
    entry_id: str,
    current_user: User = Depends(require_permission("journal:read"))
):
    """Obtener asiento contable por ID"""
    entry = await JournalEntry.get(entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asiento contable no encontrado"
        )
    
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and entry.company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a este asiento"
        )
    
    return JournalEntryResponse(
        id=str(entry.id),
        entry_number=entry.entry_number,
        document_type_id=getattr(entry, "document_type_id", None),
        document_type_code=getattr(entry, "document_type_code", None),
        date=entry.date,
        description=entry.description,
        entry_type=entry.entry_type,
        status=entry.status,
        lines=entry.lines,
        total_debit=entry.total_debit,
        total_credit=entry.total_credit,
        company_id=entry.company_id,
        created_by=entry.created_by,
        approved_by=entry.approved_by,
        approved_at=entry.approved_at,
        created_at=entry.created_at,
        updated_at=entry.updated_at
    )

@router.post("/", response_model=JournalEntryResponse)
async def create_journal_entry(
    entry_data: JournalEntryCreate,
    request: Request,
    company_id: str = Query(..., description="ID de la empresa"),
    current_user: User = Depends(require_permission("journal:create"))
):
    """Crear nuevo asiento contable"""
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta empresa"
        )
    
    # Validar doble partida
    total_debit = sum(line.debit for line in entry_data.lines)
    total_credit = sum(line.credit for line in entry_data.lines)
    
    if abs(total_debit - total_credit) > 0.01:  # Tolerancia de 1 centavo
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El asiento no está balanceado. Débitos y créditos deben ser iguales"
        )
    
    # Usar el número de asiento provisto (reservado) y validar unicidad por empresa
    entry_number = entry_data.entry_number
    if not entry_number or "-" not in entry_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="entry_number inválido o no provisto"
        )

    exists = await JournalEntry.find_one({
        "company_id": company_id,
        "entry_number": entry_number
    })
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Número de asiento ya existe para la empresa"
        )
    
    # Crear nuevo asiento
    new_entry = JournalEntry(
        entry_number=entry_number,
        document_type_id=entry_data.document_type_id,
        document_type_code=entry_data.document_type_code,
        date=entry_data.date,
        description=entry_data.description,
        entry_type=entry_data.entry_type,
        lines=entry_data.lines,
        total_debit=total_debit,
        total_credit=total_credit,
        company_id=company_id,
        created_by=str(current_user.id)
    )
    
    await new_entry.insert()

    # Marcar reserva como usada si existe
    try:
        await DocumentNumberReservation.find_one(
            DocumentNumberReservation.company_id == company_id,
            DocumentNumberReservation.number == entry_number,
            DocumentNumberReservation.status == ReservationStatus.RESERVED
        ).update({
            "$set": {
                "status": ReservationStatus.USED,
                "journal_entry_id": str(new_entry.id),
                "used_at": datetime.now()
            }
        })
    except Exception:
        pass
    
    # Log de auditoría
    await log_audit(
        user=current_user,
        action=AuditAction.CREATE,
        module=AuditModule.JOURNAL,
        description=f"Asiento contable creado: {new_entry.entry_number}",
        resource_id=str(new_entry.id),
        resource_type="journal_entry",
        new_values={
            "entry_number": new_entry.entry_number,
            "description": new_entry.description,
            "total_debit": new_entry.total_debit,
            "total_credit": new_entry.total_credit
        },
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "Unknown")
    )
    
    return JournalEntryResponse(
        id=str(new_entry.id),
        entry_number=new_entry.entry_number,
        document_type_id=new_entry.document_type_id,
        document_type_code=new_entry.document_type_code,
        date=new_entry.date,
        description=new_entry.description,
        entry_type=new_entry.entry_type,
        status=new_entry.status,
        lines=new_entry.lines,
        total_debit=new_entry.total_debit,
        total_credit=new_entry.total_credit,
        company_id=new_entry.company_id,
        created_by=new_entry.created_by,
        approved_by=new_entry.approved_by,
        approved_at=new_entry.approved_at,
        created_at=new_entry.created_at,
        updated_at=new_entry.updated_at
    )

@router.put("/{entry_id}/", response_model=JournalEntryResponse)
async def update_journal_entry(
    entry_id: str,
    entry_update: JournalEntryUpdate,
    request: Request,
    current_user: User = Depends(require_permission("journal:update"))
):
    """Actualizar asiento contable"""
    entry = await JournalEntry.get(entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asiento contable no encontrado"
        )
    
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and entry.company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a este asiento"
        )
    
    # Verificar que el asiento no esté aprobado
    if entry.status == "posted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede modificar un asiento ya aprobado"
        )
    
    # Guardar valores antiguos para auditoría
    old_values = {
        "description": entry.description,
        "date": entry.date.isoformat(),
        "lines": [line.dict() for line in entry.lines],
        "total_debit": entry.total_debit,
        "total_credit": entry.total_credit
    }
    
    # Actualizar campos
    update_data = entry_update.dict(exclude_unset=True)
    
    # Si se actualizan las líneas, validar doble partida
    if "lines" in update_data:
        total_debit = sum(line["debit"] for line in update_data["lines"])
        total_credit = sum(line["credit"] for line in update_data["lines"])
        
        if abs(total_debit - total_credit) > 0.01:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El asiento no está balanceado. Débitos y créditos deben ser iguales"
            )
        
        entry.total_debit = total_debit
        entry.total_credit = total_credit
    
    for field, value in update_data.items():
        if field != "lines":
            setattr(entry, field, value)
        else:
            entry.lines = [JournalLine(**line) for line in value]
    
    entry.updated_at = datetime.now()
    await entry.save()
    
    # Log de auditoría
    await log_audit(
        user=current_user,
        action=AuditAction.UPDATE,
        module=AuditModule.JOURNAL,
        description=f"Asiento contable actualizado: {entry.entry_number}",
        resource_id=str(entry.id),
        resource_type="journal_entry",
        old_values=old_values,
        new_values=update_data,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "Unknown")
    )
    
    return JournalEntryResponse(
        id=str(entry.id),
        entry_number=entry.entry_number,
        document_type_id=getattr(entry, "document_type_id", None),
        document_type_code=getattr(entry, "document_type_code", None),
        date=entry.date,
        description=entry.description,
        entry_type=entry.entry_type,
        status=entry.status,
        lines=entry.lines,
        total_debit=entry.total_debit,
        total_credit=entry.total_credit,
        company_id=entry.company_id,
        created_by=entry.created_by,
        approved_by=entry.approved_by,
        approved_at=entry.approved_at,
        created_at=entry.created_at,
        updated_at=entry.updated_at
    )

@router.post("/{entry_id}/approve/", response_model=JournalEntryResponse)
async def approve_journal_entry(
    entry_id: str,
    approval_data: JournalEntryApprove,
    request: Request,
    current_user: User = Depends(require_permission("journal:approve"))
):
    """Aprobar o rechazar asiento contable"""
    entry = await JournalEntry.get(entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asiento contable no encontrado"
        )
    
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and entry.company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a este asiento"
        )
    
    # Verificar que el asiento no esté ya aprobado
    if entry.status == "posted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El asiento ya está aprobado"
        )
    
    # Actualizar estado
    if approval_data.approved:
        entry.status = "posted"
        entry.approved_by = str(current_user.id)
        entry.approved_at = datetime.now()
    else:
        entry.status = "draft"
        entry.approved_by = None
        entry.approved_at = None
    
    entry.updated_at = datetime.now()
    await entry.save()
    
    # Log de auditoría
    action = AuditAction.APPROVE if approval_data.approved else AuditAction.REJECT
    await log_audit(
        user=current_user,
        action=action,
        module=AuditModule.JOURNAL,
        description=f"Asiento contable {'aprobado' if approval_data.approved else 'rechazado'}: {entry.entry_number}",
        resource_id=str(entry.id),
        resource_type="journal_entry",
        new_values={
            "status": entry.status.value,
            "approved_by": entry.approved_by,
            "approved_at": entry.approved_at.isoformat() if entry.approved_at else None,
            "notes": approval_data.notes
        },
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "Unknown")
    )
    
    return JournalEntryResponse(
        id=str(entry.id),
        entry_number=entry.entry_number,
        date=entry.date,
        description=entry.description,
        entry_type=entry.entry_type,
        status=entry.status,
        lines=entry.lines,
        total_debit=entry.total_debit,
        total_credit=entry.total_credit,
        company_id=entry.company_id,
        created_by=entry.created_by,
        approved_by=entry.approved_by,
        approved_at=entry.approved_at,
        created_at=entry.created_at,
        updated_at=entry.updated_at
    )

@router.delete("/{entry_id}/")
async def delete_journal_entry(
    entry_id: str,
    request: Request,
    current_user: User = Depends(require_permission("journal:delete"))
):
    """Eliminar asiento contable"""
    entry = await JournalEntry.get(entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asiento contable no encontrado"
        )
    
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and entry.company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a este asiento"
        )
    
    # Verificar que el asiento no esté aprobado
    if entry.status == "posted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar un asiento ya aprobado"
        )
    
    # Eliminar asiento
    await entry.delete()
    
    # Log de auditoría
    await log_audit(
        user=current_user,
        action=AuditAction.DELETE,
        module=AuditModule.JOURNAL,
        description=f"Asiento contable eliminado: {entry.entry_number}",
        resource_id=str(entry.id),
        resource_type="journal_entry",
        old_values={
            "entry_number": entry.entry_number,
            "description": entry.description,
            "status": entry.status.value
        },
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "Unknown")
    )
    
    return {"message": "Asiento contable eliminado exitosamente"}

@router.post("/{entry_id}/post/", response_model=JournalEntryResponse)
async def post_journal_entry(
    entry_id: str,
    request: Request,
    current_user: User = Depends(require_permission("journal:approve"))
):
    """Mayorizar un asiento contable (aplicar a las cuentas)"""
    entry = await JournalEntry.get(entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asiento contable no encontrado"
        )
    
    # Verificar que el asiento esté en estado DRAFT
    if entry.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden mayorizar asientos en estado DRAFT"
        )
    
    # Mayorizar el asiento
    success = await LedgerService.post_journal_entry(
        entry, 
        entry.company_id, 
        str(current_user.id)
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al mayorizar el asiento"
        )
    
    # Log de auditoría
    await log_audit(
        user=current_user,
        action=AuditAction.UPDATE,
        module=AuditModule.JOURNAL,
        description=f"Asiento contable mayorizado: {entry.entry_number}",
        resource_id=str(entry.id),
        resource_type="journal_entry",
        new_values={"status": "posted"},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "Unknown")
    )
    
    # Obtener el asiento actualizado
    updated_entry = await JournalEntry.get(entry_id)
    return JournalEntryResponse(
        id=str(updated_entry.id),
        entry_number=updated_entry.entry_number,
        document_type_id=getattr(updated_entry, "document_type_id", None),
        document_type_code=getattr(updated_entry, "document_type_code", None),
        date=updated_entry.date,
        description=updated_entry.description,
        entry_type=updated_entry.entry_type,
        status=updated_entry.status,
        lines=updated_entry.lines,
        total_debit=updated_entry.total_debit,
        total_credit=updated_entry.total_credit,
        company_id=updated_entry.company_id,
        created_by=updated_entry.created_by,
        approved_by=updated_entry.approved_by,
        approved_at=updated_entry.approved_at,
        created_at=updated_entry.created_at,
        updated_at=updated_entry.updated_at
    )

@router.post("/{entry_id}/unpost/", response_model=JournalEntryResponse)
async def unpost_journal_entry(
    entry_id: str,
    request: Request,
    current_user: User = Depends(require_permission("journal:approve"))
):
    """Desmayorizar un asiento contable (volver a estado draft)"""
    entry = await JournalEntry.get(entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asiento contable no encontrado"
        )
    
    # Verificar que el asiento esté POSTED
    if entry.status != "posted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden desmayorizar asientos mayorizados"
        )
    
    # Desmayorizar usando el LedgerService
    success = await LedgerService.unpost_journal_entry(
        entry, 
        entry.company_id, 
        str(current_user.id)
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al desmayorizar el asiento"
        )
    
    # Log de auditoría
    await log_audit(
        user=current_user,
        action=AuditAction.UPDATE,
        module=AuditModule.JOURNAL,
        description=f"Asiento contable desmayorizado: {entry.entry_number}",
        resource_id=str(entry.id),
        resource_type="journal_entry",
        old_values={"status": "posted"},
        new_values={"status": "draft"},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "Unknown")
    )
    
    return JournalEntryResponse(
        id=str(entry.id),
        entry_number=entry.entry_number,
        document_type_id=getattr(entry, "document_type_id", None),
        document_type_code=getattr(entry, "document_type_code", None),
        date=entry.date,
        description=entry.description,
        entry_type=entry.entry_type,
        status=entry.status,
        lines=entry.lines,
        total_debit=entry.total_debit,
        total_credit=entry.total_credit,
        company_id=entry.company_id,
        created_by=entry.created_by,
        approved_by=entry.approved_by,
        approved_at=entry.approved_at,
        created_at=entry.created_at,
        updated_at=entry.updated_at
    )

@router.post("/{entry_id}/copy/", response_model=JournalEntryResponse)
async def copy_journal_entry(
    entry_id: str,
    request: Request,
    current_user: User = Depends(require_permission("journal:create"))
):
    """Crear una copia de un asiento contable"""
    original_entry = await JournalEntry.get(entry_id)
    if not original_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asiento contable no encontrado"
        )
    
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and original_entry.company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a este asiento"
        )
    
    # Generar número de asiento para la copia
    last_entry = await JournalEntry.find(
        JournalEntry.company_id == original_entry.company_id
    ).sort("-entry_number").limit(1).to_list()
    
    if last_entry:
        last_number = int(last_entry[0].entry_number.split("-")[-1])
        entry_number = f"AS-{datetime.now().year}-{last_number + 1:06d}"
    else:
        entry_number = f"AS-{datetime.now().year}-000001"
    
    # Crear copia del asiento
    copied_entry = JournalEntry(
        entry_number=entry_number,
        date=original_entry.date,
        description=f"COPIA - {original_entry.description}",
        entry_type=original_entry.entry_type,
        lines=original_entry.lines,
        total_debit=original_entry.total_debit,
        total_credit=original_entry.total_credit,
        company_id=original_entry.company_id,
        created_by=str(current_user.id),
        status="draft"  # La copia siempre empieza en draft
    )
    
    await copied_entry.insert()
    
    # Log de auditoría
    await log_audit(
        user=current_user,
        action=AuditAction.CREATE,
        module=AuditModule.JOURNAL,
        description=f"Asiento contable copiado: {copied_entry.entry_number} (original: {original_entry.entry_number})",
        resource_id=str(copied_entry.id),
        resource_type="journal_entry",
        new_values={
            "entry_number": copied_entry.entry_number,
            "description": copied_entry.description,
            "original_entry_id": str(original_entry.id),
            "original_entry_number": original_entry.entry_number
        },
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "Unknown")
    )
    
    return JournalEntryResponse(
        id=str(copied_entry.id),
        entry_number=copied_entry.entry_number,
        date=copied_entry.date,
        description=copied_entry.description,
        entry_type=copied_entry.entry_type,
        status=copied_entry.status,
        lines=copied_entry.lines,
        total_debit=copied_entry.total_debit,
        total_credit=copied_entry.total_credit,
        company_id=copied_entry.company_id,
        created_by=copied_entry.created_by,
        approved_by=copied_entry.approved_by,
        approved_at=copied_entry.approved_at,
        created_at=copied_entry.created_at,
        updated_at=copied_entry.updated_at
    )

@router.post("/{entry_id}/reverse/")
async def reverse_journal_entry(
    entry_id: str,
    request: Request,
    current_user: User = Depends(require_permission("journal:approve"))
):
    """Revertir un asiento contable"""
    entry = await JournalEntry.get(entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asiento contable no encontrado"
        )
    
    # Verificar que el asiento esté POSTED
    if entry.status != "posted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden revertir asientos mayorizados"
        )
    
    # Revertir el asiento
    success = await LedgerService.reverse_journal_entry(
        entry, 
        entry.company_id, 
        str(current_user.id)
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al revertir el asiento"
        )
    
    # Log de auditoría
    await log_audit(
        user=current_user,
        action=AuditAction.UPDATE,
        module=AuditModule.JOURNAL,
        description=f"Asiento contable revertido: {entry.entry_number}",
        resource_id=str(entry.id),
        resource_type="journal_entry",
        new_values={"status": "reversed"},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "Unknown")
    )
    
    return {"message": "Asiento contable revertido exitosamente"}
