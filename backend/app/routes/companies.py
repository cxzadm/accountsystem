from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from typing import List, Optional
from app.models.company import Company, CompanyCreate, CompanyUpdate, CompanyResponse
from app.models.user import User
from app.models.account import Account
from app.models.journal import JournalEntry
from app.models.ledger import LedgerEntry
from app.models.document_type import DocumentType
from app.models.document_reservation import DocumentNumberReservation
from app.auth.dependencies import get_current_user, require_permission, log_audit, AuditAction, AuditModule
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

router = APIRouter()

async def delete_company_related_data(company_id: str) -> dict:
    """
    Elimina todos los datos relacionados con una empresa
    """
    try:
        # Conectar a la base de datos
        client = AsyncIOMotorClient(settings.mongodb_url)
        db = client[settings.database_name]
        
        deleted_counts = {}
        
        # 1. Eliminar Cuentas (Accounts)
        accounts_result = await Account.find(Account.company_id == company_id).delete()
        deleted_counts['accounts'] = accounts_result.deleted_count
        print(f"🗑️  Eliminadas {accounts_result.deleted_count} cuentas relacionadas")
        
        # 2. Eliminar Asientos Contables (Journal Entries)
        journal_entries_result = await JournalEntry.find(JournalEntry.company_id == company_id).delete()
        deleted_counts['journal_entries'] = journal_entries_result.deleted_count
        print(f"🗑️  Eliminados {journal_entries_result.deleted_count} asientos contables")
        
        # 3. Eliminar Entradas del Mayor (Ledger Entries)
        ledger_entries_result = await LedgerEntry.find(LedgerEntry.company_id == company_id).delete()
        deleted_counts['ledger_entries'] = ledger_entries_result.deleted_count
        print(f"🗑️  Eliminadas {ledger_entries_result.deleted_count} entradas del mayor")
        
        # 4. Eliminar Tipos de Documento
        document_types_result = await DocumentType.find(DocumentType.company_id == company_id).delete()
        deleted_counts['document_types'] = document_types_result.deleted_count
        print(f"🗑️  Eliminados {document_types_result.deleted_count} tipos de documento")
        
        # 5. Eliminar Reservas de Números de Documento
        document_reservations_result = await DocumentNumberReservation.find(DocumentNumberReservation.company_id == company_id).delete()
        deleted_counts['document_reservations'] = document_reservations_result.deleted_count
        print(f"🗑️  Eliminadas {document_reservations_result.deleted_count} reservas de documentos")
        
        # 6. Eliminar usuarios asociados a la empresa (remover empresa de la lista)
        users_collection = db['users']
        users_with_company = users_collection.find({"companies": ObjectId(company_id)})
        users_count = 0
        async for user_doc in users_with_company:
            # Remover la empresa de la lista de empresas del usuario
            updated_companies = [comp_id for comp_id in user_doc.get('companies', []) if comp_id != ObjectId(company_id)]
            await users_collection.update_one(
                {"_id": user_doc['_id']},
                {"$set": {"companies": updated_companies}}
            )
            users_count += 1
        deleted_counts['users_updated'] = users_count
        print(f"🔧 Actualizados {users_count} usuarios (removida empresa de la lista)")
        
        # 7. Eliminar logs de auditoría relacionados
        audit_collection = db['audit_logs']
        audit_result = await audit_collection.delete_many({
            "$or": [
                {"resource_type": "company", "resource_id": company_id},
                {"resource_type": {"$in": ["account", "journal_entry", "ledger_entry", "document_type"]},
                 "company_id": company_id}
            ]
        })
        deleted_counts['audit_logs'] = audit_result.deleted_count
        print(f"🗑️  Eliminados {audit_result.deleted_count} logs de auditoría")
        
        client.close()
        
        return deleted_counts
        
    except Exception as e:
        print(f"❌ Error eliminando datos relacionados: {e}")
        raise e

@router.get("/", response_model=List[CompanyResponse])
async def get_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_permission("companies:read"))
):
    """Obtener lista de empresas con filtros"""
    query = {}
    
    # Filtrar por empresas del usuario si no es admin
    if current_user.role != "admin":
        query["_id"] = {"$in": [ObjectId(company_id) for company_id in current_user.companies]}
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"ruc": {"$regex": search, "$options": "i"}},
            {"legal_name": {"$regex": search, "$options": "i"}}
        ]
    
    if status:
        query["status"] = status
    
    companies = await Company.find(query).skip(skip).limit(limit).to_list()
    
    return [
        CompanyResponse(
            id=str(company.id),
            name=company.name,
            ruc=company.ruc,
            legal_name=company.legal_name,
            address=company.address,
            phone=company.phone,
            email=company.email,
            status=company.status,
            fiscal_year_start=company.fiscal_year_start,
            currency=company.currency,
            created_at=company.created_at,
            updated_at=company.updated_at
        )
        for company in companies
    ]

@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: str,
    current_user: User = Depends(require_permission("companies:read"))
):
    """Obtener empresa por ID"""
    from bson import ObjectId
    try:
        company = await Company.find_one(Company.id == ObjectId(company_id))
    except Exception:
        company = None
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada"
        )
    
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta empresa"
        )
    
    return CompanyResponse(
        id=str(company.id),
        name=company.name,
        ruc=company.ruc,
        legal_name=company.legal_name,
        address=company.address,
        phone=company.phone,
        email=company.email,
        status=company.status,
        fiscal_year_start=company.fiscal_year_start,
        currency=company.currency,
        created_at=company.created_at,
        updated_at=company.updated_at
    )

@router.post("/", response_model=CompanyResponse)
async def create_company(
    company_data: CompanyCreate,
    request: Request,
    current_user: User = Depends(require_permission("companies:create"))
):
    """Crear nueva empresa"""
    # Verificar si el RUC ya existe
    existing_company = await Company.find_one(Company.ruc == company_data.ruc)
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una empresa con este RUC"
        )
    
    # Crear nueva empresa
    new_company = Company(
        name=company_data.name,
        ruc=company_data.ruc,
        legal_name=company_data.legal_name,
        address=company_data.address,
        phone=company_data.phone,
        email=company_data.email,
        fiscal_year_start=company_data.fiscal_year_start,
        currency=company_data.currency,
        created_by=current_user.id
    )
    
    await new_company.insert()
    
    # Agregar empresa a la lista del usuario
    if str(new_company.id) not in current_user.companies:
        current_user.companies.append(str(new_company.id))
        await current_user.save()
    
    # Log de auditoría
    await log_audit(
        user=current_user,
        action=AuditAction.CREATE,
        module=AuditModule.COMPANIES,
        description=f"Empresa creada: {new_company.name}",
        resource_id=str(new_company.id),
        resource_type="company",
        new_values={
            "name": new_company.name,
            "ruc": new_company.ruc,
            "legal_name": new_company.legal_name
        },
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "Unknown")
    )
    
    return CompanyResponse(
        id=str(new_company.id),
        name=new_company.name,
        ruc=new_company.ruc,
        legal_name=new_company.legal_name,
        address=new_company.address,
        phone=new_company.phone,
        email=new_company.email,
        status=new_company.status,
        fiscal_year_start=new_company.fiscal_year_start,
        currency=new_company.currency,
        created_at=new_company.created_at,
        updated_at=new_company.updated_at
    )

@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: str,
    company_update: CompanyUpdate,
    request: Request,
    current_user: User = Depends(require_permission("companies:update"))
):
    """Actualizar empresa"""
    from bson import ObjectId
    try:
        company = await Company.find_one(Company.id == ObjectId(company_id))
    except Exception:
        company = None
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada"
        )
    
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta empresa"
        )
    
    # Guardar valores antiguos para auditoría
    old_values = {
        "name": company.name,
        "ruc": company.ruc,
        "legal_name": company.legal_name,
        "address": company.address,
        "phone": company.phone,
        "email": company.email,
        "status": company.status.value,
        "fiscal_year_start": company.fiscal_year_start,
        "currency": company.currency
    }
    
    # Actualizar campos
    update_data = company_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(company, field, value)
    
    company.updated_at = datetime.now()
    await company.save()
    
    # Log de auditoría
    await log_audit(
        user=current_user,
        action=AuditAction.UPDATE,
        module=AuditModule.COMPANIES,
        description=f"Empresa actualizada: {company.name}",
        resource_id=str(company.id),
        resource_type="company",
        old_values=old_values,
        new_values=update_data,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "Unknown")
    )
    
    return CompanyResponse(
        id=str(company.id),
        name=company.name,
        ruc=company.ruc,
        legal_name=company.legal_name,
        address=company.address,
        phone=company.phone,
        email=company.email,
        status=company.status,
        fiscal_year_start=company.fiscal_year_start,
        currency=company.currency,
        created_at=company.created_at,
        updated_at=company.updated_at
    )

@router.delete("/{company_id}")
async def delete_company(
    company_id: str,
    request: Request,
    force_delete: bool = False,
    current_user: User = Depends(require_permission("companies:delete"))
):
    """Eliminar empresa (soft delete por defecto, eliminación completa si force_delete=True)"""
    from bson import ObjectId
    try:
        company = await Company.find_one(Company.id == ObjectId(company_id))
    except Exception:
        company = None
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada"
        )
    
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta empresa"
        )
    
    # Guardar información de la empresa para auditoría
    company_name = company.name
    company_data = {
        "name": company.name,
        "ruc": company.ruc,
        "legal_name": company.legal_name,
        "address": company.address,
        "phone": company.phone,
        "email": company.email,
        "status": company.status.value,
        "fiscal_year_start": company.fiscal_year_start,
        "currency": company.currency
    }
    
    if force_delete:
        # Eliminación completa - eliminar empresa y todos sus datos relacionados
        print(f"🔥 FORCE DELETE: Eliminando completamente la empresa {company_name} y todos sus datos relacionados")
        
        # Aquí eliminamos todos los datos relacionados
        deleted_data = await delete_company_related_data(company_id)
        
        # Eliminar la empresa de la base de datos
        await company.delete()
        
        # Log de auditoría
        await log_audit(
            user=current_user,
            action=AuditAction.DELETE,
            module=AuditModule.COMPANIES,
            description=f"Empresa eliminada COMPLETAMENTE: {company_name} (Force Delete)",
            resource_id=str(company.id),
            resource_type="company",
            old_values=company_data,
            new_values=None,  # Empresa completamente eliminada
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", "Unknown")
        )
        
        return {
            "message": f"Empresa '{company_name}' eliminada COMPLETAMENTE del sistema",
            "deleted_data": deleted_data
        }
    
    else:
        # Soft delete - cambiar status a inactive (comportamiento actual)
        company.status = "inactive"
        company.updated_at = datetime.now()
        await company.save()
        
        # Log de auditoría
        await log_audit(
            user=current_user,
            action=AuditAction.DELETE,
            module=AuditModule.COMPANIES,
            description=f"Empresa inactivada: {company_name} (Soft Delete)",
            resource_id=str(company.id),
            resource_type="company",
            old_values={"status": "active"},
            new_values={"status": "inactive"},
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", "Unknown")
        )
        
        return {
            "message": f"Empresa '{company_name}' inactivada exitosamente",
            "soft_delete": True,
            "can_reactivate": True
        }
