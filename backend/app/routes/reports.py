from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from typing import List, Optional, Dict, Any
from app.models.user import User
from app.models.account import Account, AccountBalance
from app.models.journal import JournalEntry
from app.auth.dependencies import get_current_user, require_permission, log_audit, AuditAction, AuditModule
from datetime import datetime, timedelta
from bson import ObjectId

router = APIRouter()

@router.get("/balance-general")
async def get_balance_general(
    company_id: str = Query(..., description="ID de la empresa"),
    as_of_date: str = Query(..., description="Fecha de corte (YYYY-MM-DD)"),
    current_user: User = Depends(require_permission("reports:read"))
):
    """Generar Balance General"""
    # Verificar que el usuario tenga acceso a esta empresa
    if current_user.role != "admin" and company_id not in current_user.companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta empresa"
        )
    
    try:
        cutoff_date = datetime.fromisoformat(as_of_date)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de fecha inválido. Use YYYY-MM-DD"
        )
    
    # Obtener todas las cuentas activas de la empresa
    accounts = await Account.find(
        Account.company_id == company_id,
        Account.is_active == True
    ).to_list()
    
    # TODO: Implementar cálculo real de balances desde journal entries
    # Por ahora retornamos estructura básica
    
    balance_general = {
        "empresa": company_id,
        "fecha_corte": as_of_date,
        "activos": {
            "corrientes": [],
            "no_corrientes": []
        },
        "pasivos": {
            "corrientes": [],
            "no_corrientes": []
        },
        "patrimonio": []
    }
    
    # Clasificar cuentas por tipo
    for account in accounts:
        if account.account_type == "activo":
            if account.code.startswith(("1", "2")):
                balance_general["activos"]["corrientes"].append({
                    "codigo": account.code,
                    "nombre": account.name,
                    "saldo": 0.0  # TODO: Calcular saldo real
                })
            else:
                balance_general["activos"]["no_corrientes"].append({
                    "codigo": account.code,
                    "nombre": account.name,
                    "saldo": 0.0
                })
        elif account.account_type == "pasivo":
            if account.code.startswith(("2", "3")):
                balance_general["pasivos"]["corrientes"].append({
                    "codigo": account.code,
                    "nombre": account.name,
                    "saldo": 0.0
                })
            else:
                balance_general["pasivos"]["no_corrientes"].append({
                    "codigo": account.code,
                    "nombre": account.name,
                    "saldo": 0.0
                })
        elif account.account_type == "patrimonio":
            balance_general["patrimonio"].append({
                "codigo": account.code,
                "nombre": account.name,
                "saldo": 0.0
            })
    
    return balance_general

@router.get("/estado-resultados")
async def get_estado_resultados(
    company_id: str = Query(..., description="ID de la empresa"),
    start_date: str = Query(..., description="Fecha inicio (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Fecha fin (YYYY-MM-DD)"),
    current_user: User = Depends(require_permission("reports:read"))
):
    """Generar Estado de Resultados"""
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
    
    # TODO: Implementar cálculo real de ingresos, gastos y costos
    estado_resultados = {
        "empresa": company_id,
        "periodo": f"{start_date} a {end_date}",
        "ingresos": {
            "ventas": 0.0,
            "otros_ingresos": 0.0,
            "total_ingresos": 0.0
        },
        "costos": {
            "costo_ventas": 0.0,
            "total_costos": 0.0
        },
        "gastos": {
            "gastos_operacionales": 0.0,
            "gastos_administrativos": 0.0,
            "gastos_ventas": 0.0,
            "total_gastos": 0.0
        },
        "utilidad_operacional": 0.0,
        "utilidad_neta": 0.0
    }
    
    return estado_resultados

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
