from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from typing import List, Optional
from app.models.account import Account, AccountCreate, AccountUpdate, AccountResponse, AccountBalance, InitialBalanceUpdate, InitialBalancesBatch, ChartOfAccountsExport, AccountType, AccountNature
from app.models.user import User
from app.auth.dependencies import get_current_user, require_permission, log_audit, AuditAction, AuditModule
from datetime import datetime
from bson import ObjectId

router = APIRouter()

@router.get("/", response_model=List[AccountResponse])
async def get_accounts(
    company_id: str = Query(..., description="ID de la empresa"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    account_type: Optional[str] = Query(None),
    is_active: Optional[str] = Query(None),
    balance_filter: Optional[str] = Query(None, description="Filter by balances: 'all', 'with-balances', 'without-balances'"),
    current_user: User = Depends(require_permission("accounts:read"))
):
    """Obtener lista de cuentas contables con filtros"""
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta empresa"
        )
    
    # Ejecutar cálculo automático de saldos padre antes de obtener las cuentas
    # Usar exactamente la misma lógica que funciona correctamente
    try:
        print(f"🔄 Ejecutando cálculo automático de saldos padre para Plan de Cuentas (lógica unificada)...")
        from app.services.ledger_service import LedgerService
        result = await LedgerService._fix_complete_hierarchy_internal(company_id)
        print(f"✅ Cálculo automático de saldos padre completado para Plan de Cuentas: {result['updated_count']} cuentas actualizadas")
    except Exception as calc_error:
        print(f"⚠️ Error en cálculo automático de saldos padre: {calc_error}")
        # No interrumpir la carga si falla el cálculo automático
    
    query = {"company_id": company_id}
    
    if search:
        query["$or"] = [
            {"code": {"$regex": search, "$options": "i"}},
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    if account_type:
        query["account_type"] = account_type
    
    if is_active is not None and is_active != "":
        query["is_active"] = is_active.lower() == "true"
    
    accounts = await Account.find(query).skip(skip).limit(limit).to_list()
    
    return [
        AccountResponse(
            id=str(account.id),
            code=account.code,
            name=account.name,
            description=account.description,
            account_type=account.account_type,
            nature=account.nature,
            parent_code=account.parent_code,
            level=account.level,
            company_id=account.company_id,
            is_active=account.is_active,
            is_editable=account.is_editable,
            initial_debit_balance=account.initial_debit_balance,
            initial_credit_balance=account.initial_credit_balance,
            current_debit_balance=account.current_debit_balance,
            current_credit_balance=account.current_credit_balance,
            last_transaction_date=account.last_transaction_date,
            created_at=account.created_at,
            updated_at=account.updated_at
        )
        for account in accounts
    ]

@router.put("/initial-balances")
async def update_initial_balances(
    balances_data: InitialBalancesBatch,
    request: Request,
    company_id: str = Query(..., description="ID de la empresa"),
    current_user: User = Depends(require_permission("accounts:update"))
):
    """Actualizar saldos iniciales de múltiples cuentas"""
    try:
        if current_user.role != "admin" and company_id not in current_user.companies:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a esta empresa"
            )

        updated_accounts = []
        errors = []

        for balance_data in balances_data.balances:
            try:
                debit = float(balance_data.initial_debit_balance or 0)
                credit = float(balance_data.initial_credit_balance or 0)

                account = await Account.find_one(
                    Account.code == balance_data.account_code,
                    Account.company_id == company_id
                )

                if not account:
                    errors.append(f"Cuenta {balance_data.account_code} no encontrada")
                    continue

                old_values = {
                    "initial_debit_balance": account.initial_debit_balance,
                    "initial_credit_balance": account.initial_credit_balance
                }

                account.initial_debit_balance = debit
                account.initial_credit_balance = credit
                account.updated_at = datetime.now()

                await account.save()
                updated_accounts.append(account.code)

                await log_audit(
                    user=current_user,
                    action=AuditAction.UPDATE,
                    module=AuditModule.ACCOUNTS,
                    description=f"Saldos iniciales actualizados para cuenta {account.code}",
                    resource_id=str(account.id),
                    resource_type="account",
                    old_values=old_values,
                    new_values={
                        "initial_debit_balance": account.initial_debit_balance,
                        "initial_credit_balance": account.initial_credit_balance
                    },
                    ip_address=request.client.host,
                    user_agent=request.headers.get("user-agent", "Unknown")
                )

            except Exception as e:
                errors.append(f"Error actualizando cuenta {balance_data.account_code}: {str(e)}")

        # Recalcular saldos de cuentas padre después de actualizar saldos iniciales
        if updated_accounts:
            try:
                from app.services.ledger_service import LedgerService
                # Obtener IDs de las cuentas actualizadas
                updated_account_objects = await Account.find(
                    Account.code.in_(updated_accounts),
                    Account.company_id == company_id
                ).to_list()
                affected_account_ids = {str(acc.id) for acc in updated_account_objects}
                await LedgerService._recalculate_parent_account_balances(affected_account_ids, company_id)
                print(f"✅ Saldos padre recalculados automáticamente para {len(updated_accounts)} cuentas actualizadas")
            except Exception as e:
                print(f"⚠️ Error al recalcular saldos padre después de actualizar saldos iniciales: {e}")

        return {
            "message": f"Saldos iniciales actualizados para {len(updated_accounts)} cuentas",
            "updated_accounts": updated_accounts,
            "errors": errors,
            "total_updated": len(updated_accounts),
            "total_errors": len(errors)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al actualizar saldos iniciales: {str(e)}")

@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: str,
    current_user: User = Depends(require_permission("accounts:read"))
):
    """Obtener cuenta contable por ID"""
    account = await Account.get(account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cuenta contable no encontrada"
        )
    
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and account.company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta cuenta"
        )
    
    return AccountResponse(
        id=str(account.id),
        code=account.code,
        name=account.name,
        description=account.description,
        account_type=account.account_type,
        nature=account.nature,
        parent_code=account.parent_code,
        level=account.level,
        company_id=account.company_id,
        is_active=account.is_active,
        is_editable=account.is_editable,
        initial_debit_balance=account.initial_debit_balance,
        initial_credit_balance=account.initial_credit_balance,
        current_debit_balance=account.current_debit_balance,
        current_credit_balance=account.current_credit_balance,
        last_transaction_date=account.last_transaction_date,
        created_at=account.created_at,
        updated_at=account.updated_at
    )

@router.post("/", response_model=AccountResponse)
async def create_account(
    account_data: AccountCreate,
    request: Request,
    company_id: str = Query(..., description="ID de la empresa"),
    current_user: User = Depends(require_permission("accounts:create"))
):
    """Crear nueva cuenta contable"""
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta empresa"
        )
    
    # Verificar si el código ya existe en esta empresa
    existing_account = await Account.find_one(
        Account.code == account_data.code,
        Account.company_id == company_id
    )
    if existing_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una cuenta con este código en esta empresa"
        )
    
    # Crear nueva cuenta
    new_account = Account(
        code=account_data.code,
        name=account_data.name,
        description=account_data.description,
        account_type=account_data.account_type,
        nature=account_data.nature,
        parent_code=account_data.parent_code,
        level=account_data.level,
        company_id=company_id,
        is_editable=account_data.is_editable,
        initial_debit_balance=account_data.initial_debit_balance,
        initial_credit_balance=account_data.initial_credit_balance,
        created_by=str(current_user.id)
    )
    
    await new_account.insert()
    
    # Recalcular saldos de cuentas padre si la nueva cuenta tiene padre
    if new_account.parent_code:
        try:
            from app.services.ledger_service import LedgerService
            affected_account_ids = {str(new_account.id)}
            await LedgerService._recalculate_parent_account_balances(affected_account_ids, company_id)
            print(f"✅ Saldos padre recalculados automáticamente para nueva cuenta: {new_account.code}")
        except Exception as e:
            print(f"⚠️ Error al recalcular saldos padre para nueva cuenta: {e}")
    
    # Log de auditoría
    await log_audit(
        user=current_user,
        action=AuditAction.CREATE,
        module=AuditModule.ACCOUNTS,
        description=f"Cuenta contable creada: {new_account.code} - {new_account.name}",
        resource_id=str(new_account.id),
        resource_type="account",
        new_values={
            "code": new_account.code,
            "name": new_account.name,
            "account_type": new_account.account_type.value
        },
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "Unknown")
    )
    
    return AccountResponse(
        id=str(new_account.id),
        code=new_account.code,
        name=new_account.name,
        description=new_account.description,
        account_type=new_account.account_type,
        nature=new_account.nature,
        parent_code=new_account.parent_code,
        level=new_account.level,
        company_id=new_account.company_id,
        is_active=new_account.is_active,
        is_editable=new_account.is_editable,
        initial_debit_balance=new_account.initial_debit_balance,
        initial_credit_balance=new_account.initial_credit_balance,
        current_debit_balance=new_account.current_debit_balance,
        current_credit_balance=new_account.current_credit_balance,
        last_transaction_date=new_account.last_transaction_date,
        created_at=new_account.created_at,
        updated_at=new_account.updated_at
    )

@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: str,
    account_update: AccountUpdate,
    request: Request,
    current_user: User = Depends(require_permission("accounts:update"))
):
    """Actualizar cuenta contable"""
    account = await Account.get(account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cuenta contable no encontrada"
        )
    
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and account.company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta cuenta"
        )
    
    # Verificar si la cuenta es editable
    if not account.is_editable:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta cuenta no es editable"
        )
    
    # Guardar valores antiguos para auditoría
    old_values = {
        "name": account.name,
        "description": account.description,
        "is_active": account.is_active,
        "is_editable": account.is_editable
    }
    
    # Actualizar campos
    update_data = account_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(account, field, value)
    
    account.updated_at = datetime.now()
    await account.save()
    
    # Log de auditoría
    await log_audit(
        user=current_user,
        action=AuditAction.UPDATE,
        module=AuditModule.ACCOUNTS,
        description=f"Cuenta contable actualizada: {account.code} - {account.name}",
        resource_id=str(account.id),
        resource_type="account",
        old_values=old_values,
        new_values=update_data,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "Unknown")
    )
    
    return AccountResponse(
        id=str(account.id),
        code=account.code,
        name=account.name,
        description=account.description,
        account_type=account.account_type,
        nature=account.nature,
        parent_code=account.parent_code,
        level=account.level,
        company_id=account.company_id,
        is_active=account.is_active,
        is_editable=account.is_editable,
        initial_debit_balance=account.initial_debit_balance,
        initial_credit_balance=account.initial_credit_balance,
        current_debit_balance=account.current_debit_balance,
        current_credit_balance=account.current_credit_balance,
        last_transaction_date=account.last_transaction_date,
        created_at=account.created_at,
        updated_at=account.updated_at
    )

@router.patch("/{account_id}/toggle-status")
async def toggle_account_status(
    account_id: str,
    request: Request,
    current_user: User = Depends(require_permission("accounts:update"))
):
    """Activar/desactivar cuenta contable"""
    account = await Account.get(account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cuenta contable no encontrada"
        )
    
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and account.company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta cuenta"
        )
    
    # Verificar si la cuenta es editable
    if not account.is_editable:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta cuenta no puede ser modificada"
        )
    
    # Toggle status
    old_status = account.is_active
    account.is_active = not account.is_active
    account.updated_at = datetime.now()
    await account.save()
    
    # Log de auditoría
    action_text = "activada" if account.is_active else "desactivada"
    await log_audit(
        user=current_user,
        action=AuditAction.UPDATE,
        module=AuditModule.ACCOUNTS,
        description=f"Cuenta contable {action_text}: {account.code} - {account.name}",
        resource_id=str(account.id),
        resource_type="account",
        old_values={"is_active": old_status},
        new_values={"is_active": account.is_active},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "Unknown")
    )
    
    return {
        "message": f"Cuenta contable {action_text} exitosamente",
        "is_active": account.is_active
    }

@router.delete("/{account_id}")
async def delete_account(
    account_id: str,
    request: Request,
    current_user: User = Depends(require_permission("accounts:delete"))
):
    """Eliminar cuenta contable (soft delete)"""
    account = await Account.get(account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cuenta contable no encontrada"
        )
    
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and account.company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta cuenta"
        )
    
    # Verificar si la cuenta es editable
    if not account.is_editable:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta cuenta no puede ser eliminada"
        )
    
    # Soft delete - cambiar is_active a False
    account.is_active = False
    account.updated_at = datetime.now()
    await account.save()
    
    # Log de auditoría
    await log_audit(
        user=current_user,
        action=AuditAction.DELETE,
        module=AuditModule.ACCOUNTS,
        description=f"Cuenta contable eliminada: {account.code} - {account.name}",
        resource_id=str(account.id),
        resource_type="account",
        old_values={"is_active": True},
        new_values={"is_active": False},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "Unknown")
    )
    
    return {"message": "Cuenta contable eliminada exitosamente"}

@router.get("/export-chart", response_model=List[ChartOfAccountsExport])
async def export_chart_of_accounts(
    company_id: str = Query(..., description="ID de la empresa"),
    current_user: User = Depends(require_permission("accounts:read"))
):
    """Exportar plan de cuentas para Excel"""
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta empresa"
        )
    
    try:
        accounts = await Account.find(
            Account.company_id == company_id,
            Account.is_active == True
        ).sort("code").to_list()
        
        return [
            ChartOfAccountsExport(
                code=account.code,
                name=account.name,
                account_type=account.account_type.value,
                nature=account.nature.value,
                initial_debit_balance=account.initial_debit_balance,
                initial_credit_balance=account.initial_credit_balance
            )
            for account in accounts
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al exportar plan de cuentas: {str(e)}"
        )

@router.post("/import-initial-balances")
async def import_initial_balances(
    balances_data: InitialBalancesBatch,
    request: Request,
    company_id: str = Query(..., description="ID de la empresa"),
    current_user: User = Depends(require_permission("accounts:update"))
):
    """Importar saldos iniciales desde Excel"""
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta empresa"
        )
    
    created_accounts = []
    updated_accounts = []
    errors = []
    
    for balance_data in balances_data.balances:
        try:
            # Buscar la cuenta por código
            account = await Account.find_one(
                Account.code == balance_data.account_code,
                Account.company_id == company_id
            )
            
            if not account:
                # Crear nueva cuenta si no existe
                new_account = Account(
                    code=balance_data.account_code,
                    name=balance_data.name or f"Cuenta {balance_data.account_code}",
                    description=balance_data.description,
                    account_type=balance_data.account_type or AccountType.ACTIVO,
                    nature=balance_data.nature or AccountNature.DEUDORA,
                    parent_code=balance_data.parent_code,
                    level=balance_data.level or 1,
                    company_id=company_id,
                    is_active=True,
                    is_editable=balance_data.is_editable or True,
                    initial_debit_balance=balance_data.initial_debit_balance or 0.0,
                    initial_credit_balance=balance_data.initial_credit_balance or 0.0,
                    current_debit_balance=balance_data.initial_debit_balance or 0.0,
                    current_credit_balance=balance_data.initial_credit_balance or 0.0,
                    created_by=str(current_user.id),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                await new_account.insert()
                created_accounts.append(new_account.code)
                
                # Log de auditoría para creación
                await log_audit(
                    user=current_user,
                    action=AuditAction.CREATE,
                    module=AuditModule.ACCOUNTS,
                    description=f"Cuenta contable creada por importación: {new_account.code} - {new_account.name}",
                    resource_id=str(new_account.id),
                    resource_type="account",
                    new_values={
                        "code": new_account.code,
                        "name": new_account.name,
                        "account_type": new_account.account_type.value
                    },
                    ip_address=request.client.host,
                    user_agent=request.headers.get("user-agent", "Unknown")
                )
            else:
                # Actualizar cuenta existente
                old_debit = account.initial_debit_balance
                old_credit = account.initial_credit_balance
                account.initial_debit_balance = balance_data.initial_debit_balance or 0.0
                account.initial_credit_balance = balance_data.initial_credit_balance or 0.0
                account.current_debit_balance = balance_data.initial_debit_balance or 0.0
                account.current_credit_balance = balance_data.initial_credit_balance or 0.0
                account.updated_at = datetime.now()
                if balance_data.name:
                    account.name = balance_data.name
                if balance_data.account_type:
                    account.account_type = balance_data.account_type
                if balance_data.nature:
                    account.nature = balance_data.nature
                if balance_data.description is not None:
                    account.description = balance_data.description
                await account.save()
                updated_accounts.append(account.code)
                
                # Log de auditoría para actualización
                await log_audit(
                    user=current_user,
                    action=AuditAction.UPDATE,
                    module=AuditModule.ACCOUNTS,
                    description=f"Saldos iniciales actualizados por importación para cuenta {account.code}",
                    resource_id=str(account.id),
                    resource_type="account",
                    old_values={
                        "initial_debit_balance": old_debit,
                        "initial_credit_balance": old_credit
                    },
                    new_values={
                        "initial_debit_balance": account.initial_debit_balance,
                        "initial_credit_balance": account.initial_credit_balance
                    },
                    ip_address=request.client.host,
                    user_agent=request.headers.get("user-agent", "Unknown")
                )
            
        except Exception as e:
            errors.append(f"Error procesando cuenta {balance_data.account_code}: {str(e)}")
    
    total_updated = len(created_accounts) + len(updated_accounts)
    
    # Log de auditoría general
    await log_audit(
        user=current_user,
        action=AuditAction.UPDATE,
        module=AuditModule.ACCOUNTS,
        description=f"Importación de saldos iniciales: {len(created_accounts)} creadas, {len(updated_accounts)} actualizadas",
        resource_id=company_id,
        resource_type="company",
        new_values={
            "created_accounts": created_accounts,
            "updated_accounts": updated_accounts,
            "total_updated": total_updated,
            "errors": errors
        },
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "Unknown")
    )
    
    # Fetch all active accounts after import for immediate frontend update
    all_accounts = await Account.find(
        Account.company_id == company_id,
        Account.is_active == True
    ).sort("code").to_list()

    accounts_response = [
        AccountResponse(
            id=str(account.id),
            code=account.code,
            name=account.name,
            description=account.description,
            account_type=account.account_type,
            nature=account.nature,
            parent_code=account.parent_code,
            level=account.level,
            company_id=account.company_id,
            is_active=account.is_active,
            is_editable=account.is_editable,
            initial_debit_balance=account.initial_debit_balance,
            initial_credit_balance=account.initial_credit_balance,
            current_debit_balance=account.current_debit_balance,
            current_credit_balance=account.current_credit_balance,
            last_transaction_date=account.last_transaction_date,
            created_at=account.created_at,
            updated_at=account.updated_at
        )
        for account in all_accounts
    ]

    return {
        "message": f"Importación completada: {len(created_accounts)} cuentas creadas, {len(updated_accounts)} actualizadas",
        "created_accounts": created_accounts,
        "updated_accounts": updated_accounts,
        "accounts": accounts_response,
        "errors": errors,
        "total_updated": total_updated,
        "total_errors": len(errors)
    }

@router.get("/{company_id}/balance", response_model=List[AccountBalance])
async def get_accounts_balance(
    company_id: str,
    start_date: Optional[str] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Fecha fin (YYYY-MM-DD)"),
    current_user: User = Depends(require_permission("accounts:read"))
):
    """Obtener balance de cuentas: saldo inicial + transacciones en rango"""
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta empresa"
        )
    
    # Parseo de fechas
    start_dt = None
    end_dt = None
    try:
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            from datetime import timedelta
            # Incluir todo el día de end_date: usamos límite exclusivo del siguiente día
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
    except Exception:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")

    # Obtener todas las cuentas activas de la empresa
    accounts = await Account.find(
        Account.company_id == company_id,
        Account.is_active == True
    ).to_list()

    # Sumar movimientos en ledger_entries por cuenta
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        from app.config import settings

        client = AsyncIOMotorClient(settings.mongodb_url)
        database = client[settings.database_name]
        collection = database.ledger_entries

        query = {"company_id": company_id}
        if start_dt:
            query["date"] = {"$gte": start_dt}
        if end_dt:
            if "date" in query:
                query["date"]["$lt"] = end_dt
            else:
                query["date"] = {"$lt": end_dt}

        pipeline = [
            {"$match": query},
            {"$group": {"_id": "$account_id", "sum_debit": {"$sum": "$debit_amount"}, "sum_credit": {"$sum": "$credit_amount"}}}
        ]
        cursor = collection.aggregate(pipeline)
        sums = await cursor.to_list(5000)
        client.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error consultando movimientos: {str(e)}")

    sums_by_account = {str(item.get("_id")): item for item in sums}

    balances: List[AccountBalance] = []
    for account in accounts:
        agg = sums_by_account.get(str(account.id), {})
        sum_debit = float(agg.get("sum_debit", 0) or 0)
        sum_credit = float(agg.get("sum_credit", 0) or 0)

        debit_balance = float(account.initial_debit_balance or 0) + sum_debit
        credit_balance = float(account.initial_credit_balance or 0) + sum_credit
        net_balance = debit_balance - credit_balance

        balances.append(
            AccountBalance(
                account=AccountResponse(
                    id=str(account.id),
                    code=account.code,
                    name=account.name,
                    description=account.description,
                    account_type=account.account_type,
                    nature=account.nature,
                    parent_code=account.parent_code,
                    level=account.level,
                    company_id=account.company_id,
                    is_active=account.is_active,
                    is_editable=account.is_editable,
                    created_at=account.created_at,
                    updated_at=account.updated_at
                ),
                debit_balance=debit_balance,
                credit_balance=credit_balance,
                net_balance=net_balance
            )
        )

    return balances

@router.post("/recalculate-parent-balances")
async def recalculate_parent_balances(
    request: Request,
    company_id: str = Query(..., description="ID de la empresa"),
    current_user: User = Depends(require_permission("accounts:update"))
):
    """Recalcular saldos de todas las cuentas padre basándose en sus cuentas hijas"""
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta empresa"
        )
    
    try:
        from app.services.ledger_service import LedgerService
        
        # Obtener todas las cuentas de la empresa
        all_accounts = await Account.find(
            Account.company_id == company_id,
            Account.is_active == True
        ).to_list()
        
        # Obtener todas las cuentas padre (que tienen cuentas hijas)
        parent_accounts = []
        for account in all_accounts:
            # Verificar si tiene cuentas hijas
            has_children = any(
                acc.parent_code == account.code or 
                (acc.code.startswith(account.code) and acc.code != account.code and len(acc.code) > len(account.code))
                for acc in all_accounts
            )
            if has_children:
                parent_accounts.append(account)
        
        print(f"🔄 Recalculando saldos de {len(parent_accounts)} cuentas padre")
        
        # Recalcular saldos para cada cuenta padre
        updated_count = 0
        for parent_account in parent_accounts:
            await LedgerService._calculate_parent_balance(parent_account, all_accounts)
            updated_count += 1
        
        # Log de auditoría
        await log_audit(
            user=current_user,
            action=AuditAction.UPDATE,
            module=AuditModule.ACCOUNTS,
            description=f"Recálculo masivo de saldos de cuentas padre completado",
            resource_id=None,
            resource_type="account_balance",
            new_values={"updated_parent_accounts": updated_count},
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", "Unknown")
        )
        
        return {
            "message": f"Saldos de {updated_count} cuentas padre recalculados exitosamente",
            "updated_count": updated_count
        }
        
    except Exception as e:
        print(f"Error al recalcular saldos de cuentas padre: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al recalcular saldos: {str(e)}"
        )

@router.post("/fix-complete-hierarchy")
async def fix_complete_hierarchy(
    request: Request,
    company_id: str = Query(..., description="ID de la empresa"),
    current_user: User = Depends(require_permission("accounts:update"))
):
    """Corregir completamente toda la jerarquía de saldos padre"""
    
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta empresa"
        )
    
    try:
        from app.services.ledger_service import LedgerService
        
        print(f"🚀 INICIANDO corrección manual de jerarquía completa para empresa {company_id}")
        
        # Usar el método interno que es exactamente el mismo que el cálculo automático
        result = await LedgerService._fix_complete_hierarchy_internal(company_id)
        updated_count = result['updated_count']
        corrections = result['corrections']
        
        print(f"🎯 CORRECCIÓN MANUAL COMPLETADA: {updated_count} cuentas padre actualizadas")
        
        # Log de auditoría
        await log_audit(
            user=current_user,
            action=AuditAction.UPDATE,
            module=AuditModule.ACCOUNTS,
            description=f"Corrección completa de jerarquía de saldos padre",
            resource_id=None,
            resource_type="account_balance",
            new_values={"updated_parent_accounts": updated_count, "corrections": corrections},
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", "Unknown")
        )
        
        return {
            "message": f"Jerarquía completa corregida: {updated_count} cuentas padre actualizadas",
            "updated_count": updated_count,
            "corrections": corrections
        }
        
    except Exception as e:
        print(f"Error al corregir jerarquía completa: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al corregir jerarquía: {str(e)}"
        )

