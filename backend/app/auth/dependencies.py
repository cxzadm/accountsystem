from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.models.user import User
from app.auth.jwt_handler import verify_token
from app.models.audit import AuditLog, AuditAction, AuditModule
from datetime import datetime

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Obtener usuario actual desde token JWT"""
    token = credentials.credentials
    payload = verify_token(token)
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    user = await User.get(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
    
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo"
        )
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Obtener usuario activo actual"""
    return current_user

def require_permission(permission: str):
    """Decorator para requerir un permiso específico"""
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if permission not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permiso requerido: {permission}"
            )
        return current_user
    return permission_checker

def require_role(required_roles: list):
    """Decorator para requerir uno de los roles especificados"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rol requerido: {', '.join(required_roles)}"
            )
        return current_user
    return role_checker

async def log_audit(
    user: User,
    action: AuditAction,
    module: AuditModule,
    description: str,
    resource_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    old_values: Optional[dict] = None,
    new_values: Optional[dict] = None,
    ip_address: str = "127.0.0.1",
    user_agent: str = "Unknown"
):
    """Registrar evento de auditoría"""
    audit_log = AuditLog(
        user_id=str(user.id),
        username=user.username,
        action=action,
        module=module,
        resource_id=resource_id,
        resource_type=resource_type,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent,
        company_id=user.companies[0] if user.companies else None,
        old_values=old_values,
        new_values=new_values
    )
    await audit_log.insert()






