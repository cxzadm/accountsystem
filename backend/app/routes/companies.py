from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from typing import List, Optional
from app.models.company import Company, CompanyCreate, CompanyUpdate, CompanyResponse
from app.models.user import User
from app.auth.dependencies import get_current_user, require_permission, log_audit, AuditAction, AuditModule
from datetime import datetime
from bson import ObjectId

router = APIRouter()

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
    company = await Company.get(company_id)
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
        created_by=str(current_user.id)
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
    company = await Company.get(company_id)
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
    current_user: User = Depends(require_permission("companies:delete"))
):
    """Eliminar empresa (soft delete)"""
    company = await Company.get(company_id)
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
    
    # Soft delete - cambiar status a inactive
    company.status = "inactive"
    company.updated_at = datetime.now()
    await company.save()
    
    # Log de auditoría
    await log_audit(
        user=current_user,
        action=AuditAction.DELETE,
        module=AuditModule.COMPANIES,
        description=f"Empresa eliminada: {company.name}",
        resource_id=str(company.id),
        resource_type="company",
        old_values={"status": "active"},
        new_values={"status": "inactive"},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "Unknown")
    )
    
    return {"message": "Empresa eliminada exitosamente"}
