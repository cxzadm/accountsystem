from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generar hash de contraseña"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crear token de acceso JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Crear token de refresh JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access"):
    """Verificar y decodificar token JWT"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tipo de token inválido"
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

def get_user_permissions(role: str) -> list:
    """Obtener permisos según el rol del usuario"""
    permissions_map = {
        "admin": [
            "users:create", "users:read", "users:update", "users:delete",
            "companies:create", "companies:read", "companies:update", "companies:delete",
            "accounts:create", "accounts:read", "accounts:update", "accounts:delete",
            "journal:create", "journal:read", "journal:update", "journal:delete", "journal:approve",
            "reports:read", "reports:export",
            "sri:read", "sri:export",
            "audit:read"
        ],
        "contador": [
            "companies:read",
            "accounts:create", "accounts:read", "accounts:update",
            "journal:create", "journal:read", "journal:update", "journal:approve",
            "reports:read", "reports:export",
            "sri:read", "sri:export"
        ],
        "auditor": [
            "journal:read",
            "reports:read", "reports:export",
            "audit:read"
        ],
        "interno": [
            "journal:read",
            "reports:read"
        ]
    }
    return permissions_map.get(role, [])
