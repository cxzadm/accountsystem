from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from typing import List, Optional, Dict, Any, Tuple
from app.models.user import User
from app.models.account import Account, AccountBalance, AccountResponse
from app.models.journal import JournalEntry
from app.auth.dependencies import get_current_user, require_permission, log_audit, AuditAction, AuditModule
from datetime import datetime, timedelta
from bson import ObjectId

router = APIRouter()

def _build_hierarchy_helpers(accounts: List[Account]) -> Tuple[Dict[str, List[Account]], Dict[str, Account]]:
    """Create helpers to identify parents/children by `parent_code` and fallback by code length pattern."""
    account_by_code: Dict[str, Account] = {a.code: a for a in accounts if a.code}
    children_by_parent: Dict[str, List[Account]] = {}
    for acc in accounts:
        if not acc.code:
            continue
        parent = acc.parent_code
        if parent:
            children_by_parent.setdefault(parent, []).append(acc)
    return children_by_parent, account_by_code

def _get_direct_children(parent_code: str, accounts: List[Account], children_by_parent: Dict[str, List[Account]]) -> List[Account]:
    """Return immediate children of a parent. Prefer `parent_code`, fallback to code-length heuristic (+2)."""
    direct = list(children_by_parent.get(parent_code, []))
    if direct:
        return direct
    # Fallback by code-length (+2)
    expected_len = len(parent_code) + 2
    return [a for a in accounts if a.code and a.code.startswith(parent_code) and len(a.code) == expected_len]

def _compute_parent_balances(accounts: List[Account], per_account_saldo: Dict[str, float]) -> Dict[str, float]:
    """Compute parent balances as sum of immediate children saldo. Leaves retain their own saldo."""
    children_by_parent, _ = _build_hierarchy_helpers(accounts)
    # We may need to compute bottom-up; sort parents by code length desc ensures children first
    by_code = {a.code: a for a in accounts if a.code}
    codes_sorted = sorted(by_code.keys(), key=lambda c: len(c), reverse=True)
    result = dict(per_account_saldo)
    for code in codes_sorted:
        parent = by_code[code]
        kids = _get_direct_children(code, accounts, children_by_parent)
        if kids:
            result[code] = sum(result.get(k.code, 0.0) for k in kids if k.code)
    return result

def _is_leaf(account: Account, accounts: List[Account], children_by_parent: Dict[str, List[Account]]) -> bool:
    if account.code in children_by_parent and children_by_parent[account.code]:
        return False
    # Fallback check by code-length heuristic
    expected_len = len(account.code or '') + 2
    return not any(a.code and a.code.startswith(account.code or '') and len(a.code) == expected_len for a in accounts)

@router.get("/balance-general")
async def get_balance_general(
    company_id: str = Query(..., description="ID de la empresa"),
    as_of_date: str = Query(..., description="Fecha de corte (YYYY-MM-DD)"),
    current_user: User = Depends(require_permission("reports:read"))
):
    """Generar Estado de Situación Financiera (Balance General) a una fecha.

    Agrupa por naturaleza del plan de cuentas mediante el primer dígito del código:
    1 Activo, 2 Pasivo, 3 Patrimonio.
    """
    if current_user.role != "admin" and company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta empresa"
        )

    try:
        cutoff = datetime.strptime(as_of_date, "%Y-%m-%d")
        inclusive_end = cutoff + timedelta(days=1)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de fecha inválido. Use YYYY-MM-DD"
        )

    # Cargar cuentas
    accounts = await Account.find(
        Account.company_id == company_id,
        Account.is_active == True
    ).to_list()

    account_by_id: Dict[str, Account] = {str(a.id): a for a in accounts}

    # Agregar movimientos hasta la fecha de corte
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        from app.config import settings
        client = AsyncIOMotorClient(settings.mongodb_url)
        db = client[settings.database_name]
        collection = db.ledger_entries

        pipeline = [
            {"$match": {
                "company_id": company_id,
                "date": {"$lt": inclusive_end}
            }},
            {"$group": {
                "_id": "$account_id",
                "sum_debit": {"$sum": {"$ifNull": ["$debit_amount", 0]}},
                "sum_credit": {"$sum": {"$ifNull": ["$credit_amount", 0]}}
            }}
        ]
        cursor = collection.aggregate(pipeline)
        sums = await cursor.to_list(10000)
        client.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error consultando movimientos: {str(e)}")

    sums_by_account: Dict[str, Dict[str, float]] = {str(doc.get("_id")): doc for doc in sums}

    # Calcular saldo por cuenta (neto) y luego recomputar saldos de padres desde sus hijas
    per_account_saldo: Dict[str, float] = {}
    for account in accounts:
        agg = sums_by_account.get(str(account.id), {})
        sum_debit = float(agg.get("sum_debit", 0) or 0)
        sum_credit = float(agg.get("sum_credit", 0) or 0)
        initial_debit = float(account.initial_debit_balance or 0)
        initial_credit = float(account.initial_credit_balance or 0)
        net_balance = (initial_debit + sum_debit) - (initial_credit + sum_credit)
        if account.code:
            per_account_saldo[account.code] = net_balance

    # Recalcular saldos de cuentas padre (sumando hijas inmediatas)
    per_account_saldo = _compute_parent_balances(accounts, per_account_saldo)

    # Helpers jerárquicos para detectar hojas y evitar doble conteo en totales
    children_by_parent, _ = _build_hierarchy_helpers(accounts)

    # Armar estructura por grupos 1,2,3
    result: Dict[str, Any] = {
        "empresa": company_id,
        "fecha_corte": as_of_date,
        "grupos": {
            "1": {"descripcion": "Activo", "cuentas": [], "total": 0.0},
            "2": {"descripcion": "Pasivo", "cuentas": [], "total": 0.0},
            "3": {"descripcion": "Patrimonio", "cuentas": [], "total": 0.0},
        }
    }

    for account in accounts:
        code = account.code or ""
        if not code:
            continue
        group = code[0]
        if group not in ("1", "2", "3"):
            continue
        net_balance = float(per_account_saldo.get(account.code, 0.0))

        result["grupos"][group]["cuentas"].append({
            "id": str(account.id),
            "codigo": account.code,
            "nombre": account.name,
            "saldo": net_balance
        })
        # Sumar al total solo si es hoja para evitar doble conteo
        if _is_leaf(account, accounts, children_by_parent):
            result["grupos"][group]["total"] += net_balance

    return result

@router.get("/estado-resultados")
async def get_estado_resultados(
    company_id: str = Query(..., description="ID de la empresa"),
    start_date: str = Query(..., description="Fecha inicio (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Fecha fin (YYYY-MM-DD)"),
    current_user: User = Depends(require_permission("reports:read"))
):
    """Generar Estado de Resultados (por período).

    Agrupa por grupos del plan: 4 Ingresos, 5 Gastos, 6 Resultados.
    """
    if current_user.role != "admin" and company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta empresa"
        )

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        inclusive_end = end + timedelta(days=1)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de fecha inválido. Use YYYY-MM-DD"
        )

    # Cargar cuentas
    accounts = await Account.find(
        Account.company_id == company_id,
        Account.is_active == True
    ).to_list()

    # Agregar movimientos del periodo
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        from app.config import settings
        client = AsyncIOMotorClient(settings.mongodb_url)
        db = client[settings.database_name]
        collection = db.ledger_entries

        pipeline = [
            {"$match": {
                "company_id": company_id,
                "date": {"$gte": start, "$lt": inclusive_end}
            }},
            {"$group": {
                "_id": "$account_id",
                "sum_debit": {"$sum": {"$ifNull": ["$debit_amount", 0]}},
                "sum_credit": {"$sum": {"$ifNull": ["$credit_amount", 0]}}
            }}
        ]
        cursor = collection.aggregate(pipeline)
        sums = await cursor.to_list(10000)
        client.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error consultando movimientos: {str(e)}")

    sums_by_account: Dict[str, Dict[str, float]] = {str(doc.get("_id")): doc for doc in sums}

    # Calcular saldo por cuenta (movimiento neto del período, sin saldos iniciales)
    per_account_saldo: Dict[str, float] = {}
    for account in accounts:
        agg = sums_by_account.get(str(account.id), {})
        sum_debit = float(agg.get("sum_debit", 0) or 0)
        sum_credit = float(agg.get("sum_credit", 0) or 0)
        group = (account.code or "")[0] if account.code else ""
        if group in ("4", "6"):
            net_movement = sum_credit - sum_debit
        else:
            net_movement = sum_debit - sum_credit
        if account.code:
            per_account_saldo[account.code] = net_movement

    # Recalcular saldos de cuentas padre (sumando hijas inmediatas)
    per_account_saldo = _compute_parent_balances(accounts, per_account_saldo)
    children_by_parent, _ = _build_hierarchy_helpers(accounts)

    result: Dict[str, Any] = {
        "empresa": company_id,
        "periodo": f"{start_date} a {end_date}",
        "grupos": {
            "4": {"descripcion": "Ingresos", "cuentas": [], "total": 0.0},
            "5": {"descripcion": "Gastos", "cuentas": [], "total": 0.0},
            "6": {"descripcion": "Resultados", "cuentas": [], "total": 0.0},
        }
    }

    for account in accounts:
        code = account.code or ""
        if not code:
            continue
        group = code[0]
        if group not in ("4", "5", "6"):
            continue
        net_movement = float(per_account_saldo.get(account.code, 0.0))

        result["grupos"][group]["cuentas"].append({
            "id": str(account.id),
            "codigo": account.code,
            "nombre": account.name,
            "saldo": net_movement
        })
        # Sumar al total solo si es hoja para evitar doble conteo
        if _is_leaf(account, accounts, children_by_parent):
            result["grupos"][group]["total"] += net_movement

    # Puede calcularse utilidad neta como total(4 y 6) - total(5)
    ingresos_total = result["grupos"]["4"]["total"] + result["grupos"]["6"]["total"]
    gastos_total = result["grupos"]["5"]["total"]
    result["utilidad_neta"] = ingresos_total - gastos_total

    return result

@router.get("/libro-mayor")
async def get_libro_mayor(
    company_id: str = Query(..., description="ID de la empresa"),
    start_date: str = Query(..., description="Fecha inicio (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Fecha fin (YYYY-MM-DD)"),
    account_code: Optional[str] = Query(None, description="Código de cuenta específica"),
    current_user: User = Depends(require_permission("reports:read"))
):
    """Generar Libro Mayor"""
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta empresa"
        )
    
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de fecha inválido. Use YYYY-MM-DD"
        )
    
    # Construir query para journal entries
    query = {
        "company_id": company_id,
        "date": {"$gte": start, "$lte": end},
        "status": "posted"
    }
    
    # Obtener asientos contables del período
    entries = await JournalEntry.find(query).to_list()
    
    # TODO: Implementar agrupación por cuenta y cálculo de movimientos
    libro_mayor = {
        "empresa": company_id,
        "periodo": f"{start_date} a {end_date}",
        "cuentas": []
    }
    
    return libro_mayor

@router.get("/auditoria")
async def get_audit_logs(
    company_id: Optional[str] = Query(None, description="ID de la empresa"),
    start_date: Optional[str] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Fecha fin (YYYY-MM-DD)"),
    user_id: Optional[str] = Query(None, description="ID del usuario"),
    action: Optional[str] = Query(None, description="Acción específica"),
    module: Optional[str] = Query(None, description="Módulo específico"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_permission("audit:read"))
):
    """Obtener logs de auditoría"""
    # Solo admin puede ver logs de auditoría
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden ver logs de auditoría"
        )
    
    from app.models.audit import AuditLog
    
    # Construir query
    query = {}
    
    if company_id:
        query["company_id"] = company_id
    
    if start_date:
        start = datetime.fromisoformat(start_date)
        query["timestamp"] = {"$gte": start}
    
    if end_date:
        end = datetime.fromisoformat(end_date)
        if "timestamp" in query:
            query["timestamp"]["$lte"] = end
        else:
            query["timestamp"] = {"$lte": end}
    
    if user_id:
        query["user_id"] = user_id
    
    if action:
        query["action"] = action
    
    if module:
        query["module"] = module
    
    # Obtener logs
    logs = await AuditLog.find(query).skip(skip).limit(limit).to_list()
    
    return {
        "logs": [
            {
                "id": str(log.id),
                "user_id": log.user_id,
                "username": log.username,
                "action": log.action.value,
                "module": log.module.value,
                "description": log.description,
                "timestamp": log.timestamp,
                "ip_address": log.ip_address,
                "company_id": log.company_id
            }
            for log in logs
        ],
        "total": len(logs)
    }

@router.post("/export/{report_type}")
async def export_report(
    report_type: str,
    request: Request,
    company_id: str = Query(..., description="ID de la empresa"),
    format: str = Query("pdf", description="Formato de exportación (pdf, excel)"),
    current_user: User = Depends(require_permission("reports:export"))
):
    """Exportar reporte en formato PDF o Excel"""
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta empresa"
        )
    
    # TODO: Implementar exportación real
    # Por ahora retornamos un mensaje de confirmación
    
    # Log de auditoría
    await log_audit(
        user=current_user,
        action=AuditAction.EXPORT,
        module=AuditModule.REPORTS,
        description=f"Reporte exportado: {report_type} en formato {format}",
        resource_id=company_id,
        resource_type="company",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "Unknown")
    )
    
    return {
        "message": f"Reporte {report_type} exportado exitosamente en formato {format}",
        "download_url": f"/api/reports/download/{report_type}_{company_id}.{format}"
    }
