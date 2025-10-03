from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from datetime import datetime, timedelta
from typing import List
from app.models.user import User, UserCreate, LoginRequest, TokenResponse, UserResponse
from app.auth.jwt_handler import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    verify_token,
    get_user_permissions
)
from app.auth.dependencies import get_current_user, log_audit, AuditAction, AuditModule
from app.config import settings

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Registrar nuevo usuario (solo admin)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden crear usuarios"
        )
    
    # Verificar si el usuario ya existe
    existing_user = await User.find_one(User.username == user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya existe"
        )
    
    existing_email = await User.find_one(User.email == user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Crear nuevo usuario
    hashed_password = get_password_hash(user_data.password)
    permissions = get_user_permissions(user_data.role.value)
    
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role=user_data.role,
        permissions=permissions,
        companies=user_data.companies,
        created_by=str(current_user.id)
    )
    
    await new_user.insert()
    
    # Log de auditoría
    await log_audit(
        user=current_user,
        action=AuditAction.CREATE,
        module=AuditModule.USERS,
        description=f"Usuario creado: {new_user.username}",
        resource_id=str(new_user.id),
        resource_type="user",
        new_values={
            "username": new_user.username,
            "email": new_user.email,
            "role": new_user.role.value
        },
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "Unknown")
    )
    
    return UserResponse(
        id=str(new_user.id),
        username=new_user.username,
        email=new_user.email,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        role=new_user.role,
        status=new_user.status,
        permissions=new_user.permissions,
        companies=new_user.companies,
        last_login=new_user.last_login,
        created_at=new_user.created_at,
        updated_at=new_user.updated_at
    )

@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, request: Request):
    """Iniciar sesión"""
    # Buscar usuario
    user = await User.find_one(User.username == credentials.username)
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )
    
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo"
        )
    
    # Actualizar último login
    user.last_login = datetime.now()
    await user.save()
    
    # Crear tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Log de auditoría
    await log_audit(
        user=user,
        action=AuditAction.LOGIN,
        module=AuditModule.AUTH,
        description="Inicio de sesión",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "Unknown")
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            status=user.status,
            permissions=user.permissions,
            companies=user.companies,
            last_login=user.last_login,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Renovar token de acceso"""
    try:
        payload = verify_token(refresh_token, "refresh")
        user_id = payload.get("sub")
        
        if str(current_user.id) != user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        # Crear nuevo token de acceso
        access_token = create_access_token(data={"sub": str(current_user.id)})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserResponse(
                id=str(current_user.id),
                username=current_user.username,
                email=current_user.email,
                first_name=current_user.first_name,
                last_name=current_user.last_name,
                role=current_user.role,
                status=current_user.status,
                permissions=current_user.permissions,
                companies=current_user.companies,
                last_login=current_user.last_login,
                created_at=current_user.created_at,
                updated_at=current_user.updated_at
            )
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de refresh inválido"
        )

@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Cerrar sesión"""
    # Log de auditoría
    await log_audit(
        user=current_user,
        action=AuditAction.LOGOUT,
        module=AuditModule.AUTH,
        description="Cierre de sesión",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "Unknown")
    )
    
    return {"message": "Sesión cerrada exitosamente"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role,
        status=current_user.status,
        permissions=current_user.permissions,
        companies=current_user.companies,
        last_login=current_user.last_login,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )

















