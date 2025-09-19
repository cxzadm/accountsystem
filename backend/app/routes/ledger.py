from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from typing import List, Optional
from app.models.ledger import AccountLedgerSummary
from app.models.journal import JournalEntry, JournalEntryResponse
from app.models.user import User
from app.auth.dependencies import get_current_user, require_permission, log_audit, AuditAction, AuditModule
from app.services.ledger_service import LedgerService
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[AccountLedgerSummary])
async def get_general_ledger(
    company_id: str = Query(..., description="ID de la empresa"),
    start_date: Optional[str] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Fecha fin (YYYY-MM-DD)"),
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
        # SOLUCIÓN ALTERNATIVA: Usar exactamente el mismo endpoint que el Plan de Cuentas
        # pero adaptado para el formato del Mayor General
        
        # 1. Ejecutar cálculo automático de saldos padre (misma lógica que Plan de Cuentas)
        try:
            print(f"🔄 Ejecutando cálculo automático de saldos padre para Mayor General (misma lógica que Plan de Cuentas)...")
            result = await LedgerService._fix_complete_hierarchy_internal(company_id)
            print(f"✅ Cálculo automático de saldos padre completado para Mayor General: {result['updated_count']} cuentas actualizadas")
        except Exception as calc_error:
            print(f"⚠️ Error en cálculo automático de saldos padre: {calc_error}")
            # No interrumpir la carga si falla el cálculo automático
        
        # 2. Obtener las cuentas usando exactamente la misma lógica que /accounts
        from app.models.account import Account
        accounts = await Account.find(
            Account.company_id == company_id,
            Account.is_active == True
        ).to_list()
        
        print(f"📊 Cuentas obtenidas con misma lógica que Plan de Cuentas: {len(accounts)}")
        
        # 3. Convertir a formato AccountLedgerSummary para mantener compatibilidad
        ledgers = []
        for account in accounts:
            # Calcular totales de movimientos si se especifican fechas
            total_debits = 0
            total_credits = 0
            entry_count = 0
            
            if start_dt or end_dt:
                # Solo calcular movimientos si se especifican fechas
                from motor.motor_asyncio import AsyncIOMotorClient
                from app.config import settings
                
                client = AsyncIOMotorClient(settings.mongodb_url)
                database = client[settings.database_name]
                collection = database.ledger_entries
                
                query = {"company_id": company_id, "account_id": str(account.id)}
                if start_dt:
                    query["date"] = {"$gte": start_dt}
                if end_dt:
                    from datetime import timedelta
                    inclusive_end = end_dt + timedelta(days=1)
                    if "date" in query:
                        query["date"]["$lt"] = inclusive_end
                    else:
                        query["date"] = {"$lt": inclusive_end}
                
                entries = await collection.find(query).to_list(1000)
                total_debits = sum(entry["debit_amount"] for entry in entries)
                total_credits = sum(entry["credit_amount"] for entry in entries)
                entry_count = len(entries)
                
                client.close()
            
            # Crear AccountLedgerSummary usando los datos de la cuenta (misma fuente que Plan de Cuentas)
            ledger_summary = AccountLedgerSummary(
                account_id=str(account.id),
                account_code=account.code,
                account_name=account.name,
                account_type=account.account_type.value,
                nature=account.nature.value,
                initial_debit_balance=account.initial_debit_balance,
                initial_credit_balance=account.initial_credit_balance,
                current_debit_balance=account.current_debit_balance,  # Misma fuente que Plan de Cuentas
                current_credit_balance=account.current_credit_balance,  # Misma fuente que Plan de Cuentas
                net_balance=account.current_debit_balance - account.current_credit_balance,
                total_debits=total_debits,
                total_credits=total_credits,
                entry_count=entry_count,
                last_transaction_date=account.last_transaction_date,
                entries=[]
            )
            
            ledgers.append(ledger_summary)
        
        print(f"✅ Mayor General creado con misma fuente de datos que Plan de Cuentas")
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
        # SOLUCIÓN ALTERNATIVA: Usar exactamente el mismo endpoint que el Plan de Cuentas
        # pero adaptado para el formato del resumen del Mayor General
        
        # 1. Ejecutar cálculo automático de saldos padre (misma lógica que Plan de Cuentas)
        try:
            print(f"🔄 Ejecutando cálculo automático de saldos padre para resumen del Mayor General (misma lógica que Plan de Cuentas)...")
            result = await LedgerService._fix_complete_hierarchy_internal(company_id)
            print(f"✅ Cálculo automático de saldos padre completado para resumen del Mayor General: {result['updated_count']} cuentas actualizadas")
        except Exception as calc_error:
            print(f"⚠️ Error en cálculo automático de saldos padre: {calc_error}")
            # No interrumpir la carga si falla el cálculo automático
        
        # 2. Obtener las cuentas usando exactamente la misma lógica que /accounts
        from app.models.account import Account
        accounts = await Account.find(
            Account.company_id == company_id,
            Account.is_active == True
        ).to_list()
        
        print(f"📊 Cuentas obtenidas con misma lógica que Plan de Cuentas: {len(accounts)}")
        
        # 3. Convertir a formato AccountLedgerSummary para mantener compatibilidad
        ledgers = []
        for account in accounts:
            # Crear AccountLedgerSummary usando los datos de la cuenta (misma fuente que Plan de Cuentas)
            ledger_summary = AccountLedgerSummary(
                account_id=str(account.id),
                account_code=account.code,
                account_name=account.name,
                account_type=account.account_type.value,
                nature=account.nature.value,
                initial_debit_balance=account.initial_debit_balance,
                initial_credit_balance=account.initial_credit_balance,
                current_debit_balance=account.current_debit_balance,  # Misma fuente que Plan de Cuentas
                current_credit_balance=account.current_credit_balance,  # Misma fuente que Plan de Cuentas
                net_balance=account.current_debit_balance - account.current_credit_balance,
                total_debits=0,  # No calcular movimientos para el resumen
                total_credits=0,
                entry_count=0,
                last_transaction_date=account.last_transaction_date,
                entries=[]
            )
            
            ledgers.append(ledger_summary)
        
        print(f"✅ Resumen del Mayor General creado con misma fuente de datos que Plan de Cuentas")
        
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



