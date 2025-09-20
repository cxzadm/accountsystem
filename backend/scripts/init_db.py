#!/usr/bin/env python3
"""
Script para inicializar la base de datos con datos de ejemplo
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings
from app.models.user import User, UserRole
from app.models.company import Company, CompanyStatus
from app.models.account import Account, AccountType, AccountNature
from app.auth.jwt_handler import get_password_hash, get_user_permissions

async def init_database():
    """Inicializar la base de datos con datos de ejemplo"""
    
    # Conectar a MongoDB
    client = AsyncIOMotorClient(settings.mongodb_url)
    database = client[settings.database_name]
    
    # Inicializar Beanie
    await init_beanie(
        database=database,
        document_models=[
            User,
            Company,
            Account
        ]
    )
    
    print("✅ Base de datos conectada")
    
    # Crear usuario administrador
    admin_user = await User.find_one(User.username == "admin")
    if not admin_user:
        admin_user = User(
            username="admin",
            email="admin@sistema-contable.com",
            password_hash=get_password_hash("admin123"),
            first_name="Administrador",
            last_name="Sistema",
            role=UserRole.ADMIN,
            permissions=get_user_permissions("admin"),
            companies=[]
        )
        await admin_user.insert()
        print("✅ Usuario administrador creado")
    else:
        print("ℹ️  Usuario administrador ya existe")
    
    # Crear usuario contador
    contador_user = await User.find_one(User.username == "contador")
    if not contador_user:
        contador_user = User(
            username="contador",
            email="contador@sistema-contable.com",
            password_hash=get_password_hash("contador123"),
            first_name="Juan",
            last_name="Pérez",
            role=UserRole.CONTADOR,
            permissions=get_user_permissions("contador"),
            companies=[]
        )
        await contador_user.insert()
        print("✅ Usuario contador creado")
    else:
        print("ℹ️  Usuario contador ya existe")
    
    # Crear empresa de ejemplo
    empresa = await Company.find_one(Company.ruc == "1234567890001")
    if not empresa:
        empresa = Company(
            name="Empresa Ejemplo S.A.",
            ruc="1234567890001",
            legal_name="Empresa Ejemplo Sociedad Anónima",
            address="Av. Amazonas N12-34, Quito, Ecuador",
            phone="+593 2 234 5678",
            email="info@empresa-ejemplo.com",
            status=CompanyStatus.ACTIVE,
            fiscal_year_start=1,
            currency="USD",
            created_by=str(admin_user.id)
        )
        await empresa.insert()
        print("✅ Empresa de ejemplo creada")
    else:
        print("ℹ️  Empresa de ejemplo ya existe")
    
    # Agregar empresa a los usuarios
    if str(empresa.id) not in admin_user.companies:
        admin_user.companies.append(str(empresa.id))
        await admin_user.save()
    
    if str(empresa.id) not in contador_user.companies:
        contador_user.companies.append(str(empresa.id))
        await contador_user.save()
    
    print("✅ Empresa asignada a usuarios")
    
    # Crear plan de cuentas básico
    plan_cuentas = [
        # Activos
        {"code": "1101", "name": "Caja", "type": AccountType.ACTIVO, "nature": AccountNature.DEUDORA},
        {"code": "1102", "name": "Bancos", "type": AccountType.ACTIVO, "nature": AccountNature.DEUDORA},
        {"code": "1201", "name": "Cuentas por Cobrar", "type": AccountType.ACTIVO, "nature": AccountNature.DEUDORA},
        {"code": "1301", "name": "Inventarios", "type": AccountType.ACTIVO, "nature": AccountNature.DEUDORA},
        {"code": "1401", "name": "Activos Fijos", "type": AccountType.ACTIVO, "nature": AccountNature.DEUDORA},
        
        # Pasivos
        {"code": "2101", "name": "Cuentas por Pagar", "type": AccountType.PASIVO, "nature": AccountNature.ACREEDORA},
        {"code": "2201", "name": "Préstamos Bancarios", "type": AccountType.PASIVO, "nature": AccountNature.ACREEDORA},
        {"code": "2301", "name": "Impuestos por Pagar", "type": AccountType.PASIVO, "nature": AccountNature.ACREEDORA},
        
        # Patrimonio
        {"code": "3101", "name": "Capital Social", "type": AccountType.PATRIMONIO, "nature": AccountNature.ACREEDORA},
        {"code": "3201", "name": "Utilidades Retenidas", "type": AccountType.PATRIMONIO, "nature": AccountNature.ACREEDORA},
        
        # Ingresos
        {"code": "4101", "name": "Ventas", "type": AccountType.INGRESOS, "nature": AccountNature.ACREEDORA},
        {"code": "4201", "name": "Otros Ingresos", "type": AccountType.INGRESOS, "nature": AccountNature.ACREEDORA},
        
        # Gastos
        {"code": "5101", "name": "Gastos Administrativos", "type": AccountType.GASTOS, "nature": AccountNature.DEUDORA},
        {"code": "5201", "name": "Gastos de Ventas", "type": AccountType.GASTOS, "nature": AccountNature.DEUDORA},
        {"code": "5301", "name": "Gastos Financieros", "type": AccountType.GASTOS, "nature": AccountNature.DEUDORA},
    ]
    
    cuentas_creadas = 0
    for cuenta_data in plan_cuentas:
        existing_account = await Account.find_one(
            Account.code == cuenta_data["code"],
            Account.company_id == str(empresa.id)
        )
        
        if not existing_account:
            account = Account(
                code=cuenta_data["code"],
                name=cuenta_data["name"],
                account_type=cuenta_data["type"],
                nature=cuenta_data["nature"],
                level=1,
                company_id=str(empresa.id),
                created_by=str(admin_user.id)
            )
            await account.insert()
            cuentas_creadas += 1
    
    if cuentas_creadas > 0:
        print(f"✅ {cuentas_creadas} cuentas contables creadas")
    else:
        print("ℹ️  Plan de cuentas ya existe")
    
    print("\n🎉 Inicialización completada exitosamente!")
    print("\nCredenciales de acceso:")
    print("👤 Admin: admin / admin123")
    print("👤 Contador: contador / contador123")
    print(f"\n🌐 Frontend: http://localhost:5173")
    print(f"🔧 Backend API: http://localhost:8000")
    print(f"📚 Documentación: http://localhost:8000/docs")

if __name__ == "__main__":
    asyncio.run(init_database())














