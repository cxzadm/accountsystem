from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from typing import List, Optional
from app.models.user import User, UserCreate, UserUpdate, UserResponse
from app.auth.dependencies import get_current_user, require_permission, log_audit, AuditAction, AuditModule
from app.auth.jwt_handler import get_password_hash, get_user_permissions
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_permission("users:read"))
):
    """Obtener lista de usuarios con filtros"""
    query = {}
    
    if search:
        query["$or"] = [
            {"username": {"$regex": search, "$options": "i"}},
            {"first_name": {"$regex": search, "$options": "i"}},
            {"last_name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]
    
    if role:
        query["role"] = role
    
    if status:
        query["status"] = status
    
    users = await User.find(query).skip(skip).limit(limit).to_list()
    
    return [
        UserResponse(
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
        for user in users
    ]

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    request: Request,
    current_user: User = Depends(require_permission("users:create"))
):
    """Crear nuevo usuario"""
    # Verificar si el username ya existe
    existing_user = await User.find_one(User.username == user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con este nombre de usuario"
        )
    
    # Verificar si el email ya existe
    existing_email = await User.find_one(User.email == user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con este email"
        )
    
    # Crear nuevo usuario
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role=user_data.role,
        status=user_data.status,
        permissions=get_user_permissions(user_data.role),
        companies=user_data.companies or [],
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
            "role": new_user.role.value,
            "status": new_user.status.value
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

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(require_permission("users:read"))
):
    """Obtener usuario por ID"""
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return UserResponse(
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

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    request: Request,
    current_user: User = Depends(require_permission("users:update"))
):
    """Actualizar usuario"""
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Guardar valores antiguos para auditoría
    old_values = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role.value,
        "status": user.status.value,
        "permissions": user.permissions,
        "companies": user.companies
    }
    
    # Actualizar campos
    update_data = user_update.dict(exclude_unset=True)
    
    if "role" in update_data:
        # Actualizar permisos según el nuevo rol
        update_data["permissions"] = get_user_permissions(update_data["role"].value)
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    user.updated_at = datetime.now()
    await user.save()
    
    # Log de auditoría
    await log_audit(
        user=current_user,
        action=AuditAction.UPDATE,
        module=AuditModule.USERS,
        description=f"Usuario actualizado: {user.username}",
        resource_id=str(user.id),
        resource_type="user",
        old_values=old_values,
        new_values=update_data,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "Unknown")
    )
    
    return UserResponse(
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

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    request: Request,
    current_user: User = Depends(require_permission("users:delete"))
):
    """Eliminar usuario (hard delete)"""
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    if str(user.id) == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tu propio usuario"
        )
    
    # Capturar datos previos para auditoría antes de eliminar
    old_values = {
        "username": user.username,
        "email": user.email,
        "role": user.role.value if hasattr(user.role, "value") else str(user.role),
        "status": user.status.value if hasattr(user.status, "value") else str(user.status)
    }
    user_id_str = str(user.id)
    username_str = user.username

    # Hard delete - eliminar documento de la base de datos
    await user.delete()
    
    # Log de auditoría
    await log_audit(
        user=current_user,
        action=AuditAction.DELETE,
        module=AuditModule.USERS,
        description=f"Usuario eliminado: {username_str}",
        resource_id=user_id_str,
        resource_type="user",
        old_values=old_values,
        new_values={"deleted": True},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "Unknown")
    )
    
    return {"message": "Usuario eliminado exitosamente"}

@router.post("/{user_id}/reset-password")
async def reset_password(
    user_id: str,
    new_password: str,
    request: Request,
    current_user: User = Depends(require_permission("users:update"))
):
    """Restablecer contraseña de usuario"""
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Actualizar contraseña
    user.password_hash = get_password_hash(new_password)
    user.updated_at = datetime.now()
    await user.save()
    
    # Log de auditoría
    await log_audit(
        user=current_user,
        action=AuditAction.UPDATE,
        module=AuditModule.USERS,
        description=f"Contraseña restablecida para: {user.username}",
        resource_id=str(user.id),
        resource_type="user",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "Unknown")
    )
    
    return {"message": "Contraseña restablecida exitosamente"}

