from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from typing import List, Optional
from app.models.ledger import AccountLedgerSummary
from app.models.journal import JournalEntry, JournalEntryResponse
from app.models.user import User
from app.auth.dependencies import get_current_user, require_permission, log_audit, AuditAction, AuditModule
from app.services.ledger_service import LedgerService
from datetime import datetime

router = APIRouter()

@router.get("/debug/", response_model=dict)
async def debug_ledger_data(
    company_id: str = Query(..., description="ID de la empresa"),
    current_user: User = Depends(require_permission("reports:read"))
):
    """Endpoint de debug para verificar datos del ledger"""
    
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta empresa"
        )
    
    try:
        from app.models.account import Account
        from app.models.journal import JournalEntry
        from app.models.ledger import LedgerEntry
        from motor.motor_asyncio import AsyncIOMotorClient
        from app.config import settings
        
        # Obtener todas las cuentas
        accounts = await Account.find(
            Account.company_id == company_id,
            Account.is_active == True
        ).to_list()
        
        # Obtener todos los asientos
        journal_entries = await JournalEntry.find(
            JournalEntry.company_id == company_id
        ).to_list()
        
        # Obtener todas las entradas del ledger
        ledger_entries = await LedgerEntry.find(
            LedgerEntry.company_id == company_id
        ).to_list()
        
        # Obtener entradas del ledger usando MongoDB directo
        client = AsyncIOMotorClient(settings.mongodb_url)
        database = client[settings.database_name]
        collection = database.ledger_entries
        mongo_ledger_entries = await collection.find({"company_id": company_id}).to_list(1000)
        client.close()
        
        return {
            "accounts_count": len(accounts),
            "accounts": [{"id": str(acc.id), "code": acc.code, "name": acc.name} for acc in accounts],
            "journal_entries_count": len(journal_entries),
            "journal_entries": [{"id": str(je.id), "entry_number": je.entry_number, "status": je.status, "lines_count": len(je.lines)} for je in journal_entries],
            "ledger_entries_count": len(ledger_entries),
            "mongo_ledger_entries_count": len(mongo_ledger_entries),
            "mongo_ledger_entries": [{"account_id": entry.get("account_id"), "account_code": entry.get("account_code"), "debit": entry.get("debit_amount"), "credit": entry.get("credit_amount")} for entry in mongo_ledger_entries[:10]]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en debug: {str(e)}")

@router.post("/sync-journal-to-ledger/", response_model=dict)
async def sync_journal_to_ledger(
    company_id: str = Query(..., description="ID de la empresa"),
    current_user: User = Depends(require_permission("reports:read"))
):
    """Sincronizar asientos aprobados con el ledger"""
    
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta empresa"
        )
    
    try:
        from app.models.journal import JournalEntry
        from app.services.ledger_service import LedgerService
        
        # Obtener asientos aprobados que no han sido mayorizados
        journal_entries = await JournalEntry.find(
            JournalEntry.company_id == company_id,
            JournalEntry.status == "posted"
        ).to_list()
        
        posted_count = 0
        errors = []
        
        for entry in journal_entries:
            try:
                # Verificar si ya tiene entradas del ledger
                from app.models.ledger import LedgerEntry
                existing_entries = await LedgerEntry.find(
                    LedgerEntry.journal_entry_id == str(entry.id)
                ).to_list()
                
                if not existing_entries:
                    # Mayorizar el asiento
                    success = await LedgerService.post_journal_entry(
                        entry, 
                        company_id, 
                        str(current_user.id)
                    )
                    if success:
                        posted_count += 1
                    else:
                        errors.append(f"Error mayorizando asiento {entry.entry_number}")
                else:
                    print(f"Asiento {entry.entry_number} ya mayorizado")
                    
            except Exception as e:
                errors.append(f"Error procesando asiento {entry.entry_number}: {str(e)}")
        
        return {
            "message": f"Sincronización completada: {posted_count} asientos mayorizados",
            "posted_count": posted_count,
            "total_entries": len(journal_entries),
            "errors": errors
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en sincronización: {str(e)}")

@router.get("/check-account/{account_code}/", response_model=dict)
async def check_account_status(
    account_code: str,
    company_id: str = Query(..., description="ID de la empresa"),
    current_user: User = Depends(require_permission("reports:read"))
):
    """Verificar el estado de una cuenta específica"""
    
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta empresa"
        )
    
    try:
        from app.models.account import Account
        from app.models.journal import JournalEntry
        from app.models.ledger import LedgerEntry
        
        # Buscar la cuenta
        account = await Account.find_one(
            Account.company_id == company_id,
            Account.code == account_code
        )
        
        if not account:
            return {
                "account_code": account_code,
                "found": False,
                "message": "Cuenta no encontrada"
            }
        
        # Buscar entradas del ledger para esta cuenta
        ledger_entries = await LedgerEntry.find(
            LedgerEntry.company_id == company_id,
            LedgerEntry.account_code == account_code
        ).to_list()
        
        # Buscar asientos que contengan esta cuenta
        journal_entries = await JournalEntry.find(
            JournalEntry.company_id == company_id,
            JournalEntry.status == "posted"
        ).to_list()
        
        journal_lines = []
        for je in journal_entries:
            for line in je.lines:
                if line.account_code == account_code:
                    journal_lines.append({
                        "entry_number": je.entry_number,
                        "date": je.date,
                        "description": line.description,
                        "debit": line.debit,
                        "credit": line.credit
                    })
        
        return {
            "account_code": account_code,
            "account_name": account.name,
            "found": True,
            "account_id": str(account.id),
            "is_active": account.is_active,
            "initial_debit_balance": account.initial_debit_balance,
            "initial_credit_balance": account.initial_credit_balance,
            "current_debit_balance": account.current_debit_balance,
            "current_credit_balance": account.current_credit_balance,
            "ledger_entries_count": len(ledger_entries),
            "journal_lines_count": len(journal_lines),
            "journal_lines": journal_lines[:5],  # Mostrar solo las primeras 5
            "ledger_entries": [{"date": le.date, "description": le.description, "debit": le.debit_amount, "credit": le.credit_amount} for le in ledger_entries[:5]]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verificando cuenta: {str(e)}")

@router.get("/test-accounts/", response_model=dict)
async def test_accounts_visibility(
    company_id: str = Query(..., description="ID de la empresa"),
    current_user: User = Depends(require_permission("reports:read"))
):
    """Probar la visibilidad de cuentas específicas en el mayor general"""
    
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta empresa"
        )
    
    try:
        from app.models.account import Account
        from app.services.ledger_service import LedgerService
        
        # Obtener todas las cuentas
        accounts = await Account.find(
            Account.company_id == company_id,
            Account.is_active == True
        ).to_list()
        
        # Obtener el mayor general
        ledger_data = await LedgerService.get_general_ledger(company_id)
        
        # Verificar cuentas específicas
        target_codes = ["101010202", "101010203", "101010201", "101010301"]
        results = {}
        
        for code in target_codes:
            # Buscar en cuentas
            account = next((acc for acc in accounts if acc.code == code), None)
            
            # Buscar en ledger
            ledger_account = next((ledger for ledger in ledger_data if ledger.account_code == code), None)
            
            results[code] = {
                "in_accounts": account is not None,
                "in_ledger": ledger_account is not None,
                "account_name": account.name if account else "No encontrada",
                "account_active": account.is_active if account else None,
                "initial_debit": account.initial_debit_balance if account else None,
                "initial_credit": account.initial_credit_balance if account else None,
                "current_debit": account.current_debit_balance if account else None,
                "current_credit": account.current_credit_balance if account else None,
                "ledger_net_balance": ledger_account.net_balance if ledger_account else None,
                "ledger_total_debits": ledger_account.total_debits if ledger_account else None,
                "ledger_total_credits": ledger_account.total_credits if ledger_account else None,
                "ledger_entry_count": ledger_account.entry_count if ledger_account else None
            }
        
        return {
            "total_accounts": len(accounts),
            "total_ledger_accounts": len(ledger_data),
            "account_codes": [acc.code for acc in accounts],
            "ledger_codes": [ledger.account_code for ledger in ledger_data],
            "target_accounts": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en prueba: {str(e)}")

@router.get("/", response_model=List[AccountLedgerSummary])
async def get_general_ledger(
    company_id: str = Query(..., description="ID de la empresa"),
    start_date: Optional[str] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Fecha fin (YYYY-MM-DD)"),
    # Parámetros de búsqueda inteligente
    search: Optional[str] = Query(None, description="Búsqueda general"),
    description: Optional[str] = Query(None, description="Buscar en descripción"),
    min_balance: Optional[float] = Query(None, description="Saldo mínimo"),
    max_balance: Optional[float] = Query(None, description="Saldo máximo"),
    exact_balance: Optional[float] = Query(None, description="Saldo exacto"),
    level: Optional[int] = Query(None, description="Nivel de cuenta"),
    nature: Optional[str] = Query(None, description="Naturaleza de cuenta"),
    parent_code: Optional[str] = Query(None, description="Código de cuenta padre"),
    document_type_code: Optional[str] = Query(None, description="Código de tipo de documento"),
    reference: Optional[str] = Query(None, description="Referencia"),
    entry_number: Optional[str] = Query(None, description="Número de asiento"),
    min_movements: Optional[int] = Query(None, description="Movimientos mínimos"),
    max_movements: Optional[int] = Query(None, description="Movimientos máximos"),
    exact_movements: Optional[int] = Query(None, description="Movimientos exactos"),
    min_value: Optional[float] = Query(None, description="Valor mínimo"),
    max_value: Optional[float] = Query(None, description="Valor máximo"),
    exact_value: Optional[float] = Query(None, description="Valor exacto"),
    current_user: User = Depends(require_permission("reports:read"))
):
    """Obtener el mayor general de todas las cuentas"""
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta empresa"
        )
    
    # Convertir fechas si se proporcionan
    start_dt = None
    end_dt = None
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de fecha inicio inválido. Use YYYY-MM-DD"
            )
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de fecha fin inválido. Use YYYY-MM-DD"
            )
    
    try:
        # Usar exactamente la misma lógica que el Plan de Cuentas
        # Ejecutar el endpoint fix-complete-hierarchy que funciona correctamente
        try:
            print(f"🔄 Ejecutando cálculo automático de saldos padre para Mayor General (misma lógica que Plan de Cuentas)...")
            result = await LedgerService._fix_complete_hierarchy_internal(company_id)
            print(f"✅ Cálculo automático de saldos padre completado para Mayor General: {result['updated_count']} cuentas actualizadas")
        except Exception as calc_error:
            print(f"⚠️ Error en cálculo automático de saldos padre: {calc_error}")
            # No interrumpir la carga si falla el cálculo automático
        
        # Ahora obtener el mayor general con los saldos ya calculados
        # Crear diccionario de filtros de búsqueda inteligente
        search_filters = {}
        if search:
            search_filters['search'] = search
        if description:
            search_filters['description'] = description
        if min_balance is not None:
            search_filters['min_balance'] = min_balance
        if max_balance is not None:
            search_filters['max_balance'] = max_balance
        if exact_balance is not None:
            search_filters['exact_balance'] = exact_balance
        if level is not None:
            search_filters['level'] = level
        if nature:
            search_filters['nature'] = nature
        if parent_code:
            search_filters['parent_code'] = parent_code
        if document_type_code:
            search_filters['document_type_code'] = document_type_code
        if reference:
            search_filters['reference'] = reference
        if entry_number:
            search_filters['entry_number'] = entry_number
        if min_movements is not None:
            search_filters['min_movements'] = min_movements
        if max_movements is not None:
            search_filters['max_movements'] = max_movements
        if exact_movements is not None:
            search_filters['exact_movements'] = exact_movements
        if min_value is not None:
            search_filters['min_value'] = min_value
        if max_value is not None:
            search_filters['max_value'] = max_value
        if exact_value is not None:
            search_filters['exact_value'] = exact_value
        
        ledgers = await LedgerService.get_general_ledger(company_id, start_dt, end_dt, search_filters)
        return ledgers
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener mayor general: {str(e)}"
        )

@router.get("/account/{account_id}", response_model=AccountLedgerSummary)
async def get_account_ledger(
    account_id: str,
    company_id: str = Query(..., description="ID de la empresa"),
    start_date: Optional[str] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Fecha fin (YYYY-MM-DD)"),
    current_user: User = Depends(require_permission("reports:read"))
):
    """Obtener el mayor de una cuenta específica"""
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta empresa"
        )
    
    # Convertir fechas si se proporcionan
    start_dt = None
    end_dt = None
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de fecha inicio inválido. Use YYYY-MM-DD"
            )
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de fecha fin inválido. Use YYYY-MM-DD"
            )
    
    try:
        ledger = await LedgerService.get_account_ledger(account_id, company_id, start_dt, end_dt)
        return ledger
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener mayor de cuenta: {str(e)}"
        )

@router.get("/account/{account_id}/entries", response_model=dict)
async def get_account_ledger_entries(
    account_id: str,
    company_id: str = Query(..., description="ID de la empresa"),
    start_date: Optional[str] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Fecha fin (YYYY-MM-DD)"),
    current_user: User = Depends(require_permission("reports:read"))
):
    """Entradas del mayor para una cuenta (respuesta simple y robusta)"""
    if current_user.role != "admin" and company_id not in current_user.companies:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso a esta empresa")

    # Parseo de fechas
    start_dt = None
    end_dt = None
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inicio inválido. Use YYYY-MM-DD")
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha fin inválido. Use YYYY-MM-DD")

    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        from app.config import settings
        from app.models.account import Account

        # Obtener cuenta
        account = await Account.get(account_id)
        if not account:
            from bson import ObjectId
            account = await Account.get(ObjectId(account_id))
        if not account:
            raise HTTPException(status_code=404, detail="Cuenta no encontrada")

        client = AsyncIOMotorClient(settings.mongodb_url)
        db = client[settings.database_name]
        col = db.ledger_entries

        query = {"company_id": company_id, "account_id": str(account.id)}
        if start_dt:
            query["date"] = {"$gte": start_dt}
        if end_dt:
            if "date" in query:
                query["date"]["$lte"] = end_dt
            else:
                query["date"] = {"$lte": end_dt}

        docs = await col.find(query).sort("date", 1).to_list(1000)
        client.close()

        # Normalizar
        entries = [
            {
                "id": str(d.get("_id")),
                "date": d.get("date"),
                "description": d.get("description"),
                "reference": d.get("reference"),
                "debit_amount": d.get("debit_amount", 0),
                "credit_amount": d.get("credit_amount", 0),
                "running_debit_balance": d.get("running_debit_balance", 0),
                "running_credit_balance": d.get("running_credit_balance", 0),
                "account_code": d.get("account_code"),
                "account_name": d.get("account_name"),
            }
            for d in docs
        ]

        return {
            "account_id": str(account.id),
            "account_code": account.code,
            "account_name": account.name,
            "initial_debit_balance": account.initial_debit_balance,
            "initial_credit_balance": account.initial_credit_balance,
            "entries": entries,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener entradas del mayor: {e}")

@router.get("/entries", response_model=List[JournalEntryResponse])
async def get_ledger_entries(
    company_id: str = Query(..., description="ID de la empresa"),
    start_date: Optional[str] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Fecha fin (YYYY-MM-DD)"),
    current_user: User = Depends(require_permission("reports:read"))
):
    """Obtener los asientos contables mayorizados (para el Mayor General)"""
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta empresa"
        )
    
    # Convertir fechas si se proporcionan
    start_dt = None
    end_dt = None
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de fecha inicio inválido. Use YYYY-MM-DD"
            )
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de fecha fin inválido. Use YYYY-MM-DD"
            )
    
    try:
        # Usar motor directo para evitar problemas con Beanie
        from motor.motor_asyncio import AsyncIOMotorClient
        from app.config import settings
        
        client = AsyncIOMotorClient(settings.mongodb_url)
        database = client[settings.database_name]
        collection = database.journal_entries
        
        # Construir query para MongoDB
        query = {
            "company_id": company_id,
            "status": "posted"
        }
        
        if start_dt:
            query["date"] = {"$gte": start_dt}
        if end_dt:
            if "date" in query:
                query["date"]["$lte"] = end_dt
            else:
                query["date"] = {"$lte": end_dt}
        
        # Obtener asientos mayorizados ordenados por fecha
        entries_cursor = collection.find(query).sort("date", -1)
        entries = await entries_cursor.to_list(1000)
        
        client.close()
        
        # Convertir a response model
        response_entries = []
        for entry in entries:
            response_entries.append(JournalEntryResponse(
                id=str(entry["_id"]),
                entry_number=entry["entry_number"],
                document_type_id=entry.get("document_type_id"),
                document_type_code=entry.get("document_type_code"),
                date=entry["date"],
                description=entry["description"],
                entry_type=entry["entry_type"],
                status=entry["status"],
                lines=entry["lines"],
                total_debit=entry["total_debit"],
                total_credit=entry["total_credit"],
                company_id=entry["company_id"],
                created_by=entry["created_by"],
                responsable=entry.get("responsable"),
                approved_by=entry.get("approved_by"),
                approved_at=entry.get("approved_at"),
                created_at=entry["created_at"],
                updated_at=entry["updated_at"]
            ))
        
        return response_entries
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener asientos del mayor: {str(e)}"
        )

@router.get("/summary", response_model=dict)
async def get_ledger_summary(
    company_id: str = Query(..., description="ID de la empresa"),
    current_user: User = Depends(require_permission("reports:read"))
):
    """Obtener resumen del mayor general"""
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta empresa"
        )
    
    try:
        # Usar exactamente la misma lógica que el Plan de Cuentas
        # Ejecutar el endpoint fix-complete-hierarchy que funciona correctamente
        try:
            print(f"🔄 Ejecutando cálculo automático de saldos padre para resumen del Mayor General (misma lógica que Plan de Cuentas)...")
            result = await LedgerService._fix_complete_hierarchy_internal(company_id)
            print(f"✅ Cálculo automático de saldos padre completado para resumen del Mayor General: {result['updated_count']} cuentas actualizadas")
        except Exception as calc_error:
            print(f"⚠️ Error en cálculo automático de saldos padre: {calc_error}")
            # No interrumpir la carga si falla el cálculo automático
        
        # Ahora obtener el resumen con los saldos ya calculados
        ledgers = await LedgerService.get_general_ledger(company_id)
        
        # Calcular totales generales
        total_debits = sum(ledger.total_debits for ledger in ledgers)
        total_credits = sum(ledger.total_credits for ledger in ledgers)
        total_balance = sum(ledger.net_balance for ledger in ledgers)
        
        # Agrupar por tipo de cuenta
        by_type = {}
        for ledger in ledgers:
            account_type = ledger.account_type
            if account_type not in by_type:
                by_type[account_type] = {
                    "count": 0,
                    "total_debits": 0,
                    "total_credits": 0,
                    "net_balance": 0
                }
            
            by_type[account_type]["count"] += 1
            by_type[account_type]["total_debits"] += ledger.total_debits
            by_type[account_type]["total_credits"] += ledger.total_credits
            by_type[account_type]["net_balance"] += ledger.net_balance
        
        return {
            "company_id": company_id,
            "total_accounts": len(ledgers),
            "total_debits": total_debits,
            "total_credits": total_credits,
            "total_balance": total_balance,
            "is_balanced": abs(total_debits - total_credits) < 0.01,
            "by_type": by_type,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener resumen del mayor: {str(e)}"
        )



