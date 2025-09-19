#!/usr/bin/env python3
"""
Script para crear un plan de cuentas de ejemplo con saldos iniciales
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
from app.models.account import Account, AccountType, AccountNature
from app.models.company import Company
from app.models.user import User

# Plan de cuentas de ejemplo
SAMPLE_CHART = [
    # ACTIVOS
    {"code": "1", "name": "ACTIVO", "type": AccountType.ACTIVO, "nature": AccountNature.DEUDORA, "level": 1},
    {"code": "11", "name": "ACTIVO CORRIENTE", "type": AccountType.ACTIVO, "nature": AccountNature.DEUDORA, "level": 2, "parent": "1"},
    {"code": "1101", "name": "CAJA", "type": AccountType.ACTIVO, "nature": AccountNature.DEUDORA, "level": 3, "parent": "11", "debit": 5000.00},
    {"code": "1102", "name": "BANCOS", "type": AccountType.ACTIVO, "nature": AccountNature.DEUDORA, "level": 3, "parent": "11", "debit": 25000.00},
    {"code": "1103", "name": "INVERSIONES TEMPORALES", "type": AccountType.ACTIVO, "nature": AccountNature.DEUDORA, "level": 3, "parent": "11", "debit": 10000.00},
    {"code": "12", "name": "CUENTAS POR COBRAR", "type": AccountType.ACTIVO, "nature": AccountNature.DEUDORA, "level": 2, "parent": "1"},
    {"code": "1201", "name": "CUENTAS POR COBRAR COMERCIALES", "type": AccountType.ACTIVO, "nature": AccountNature.DEUDORA, "level": 3, "parent": "12", "debit": 15000.00},
    {"code": "1202", "name": "CUENTAS POR COBRAR NO COMERCIALES", "type": AccountType.ACTIVO, "nature": AccountNature.DEUDORA, "level": 3, "parent": "12", "debit": 5000.00},
    {"code": "13", "name": "INVENTARIOS", "type": AccountType.ACTIVO, "nature": AccountNature.DEUDORA, "level": 2, "parent": "1"},
    {"code": "1301", "name": "MERCADERÍAS", "type": AccountType.ACTIVO, "nature": AccountNature.DEUDORA, "level": 3, "parent": "13", "debit": 30000.00},
    {"code": "1302", "name": "MATERIA PRIMA", "type": AccountType.ACTIVO, "nature": AccountNature.DEUDORA, "level": 3, "parent": "13", "debit": 20000.00},
    {"code": "14", "name": "ACTIVO NO CORRIENTE", "type": AccountType.ACTIVO, "nature": AccountNature.DEUDORA, "level": 2, "parent": "1"},
    {"code": "1401", "name": "INMUEBLES, PLANTA Y EQUIPO", "type": AccountType.ACTIVO, "nature": AccountNature.DEUDORA, "level": 3, "parent": "14", "debit": 100000.00},
    {"code": "1402", "name": "DEPRECIACIÓN ACUMULADA", "type": AccountType.ACTIVO, "nature": AccountNature.ACREEDORA, "level": 3, "parent": "14", "credit": 20000.00},
    
    # PASIVOS
    {"code": "2", "name": "PASIVO", "type": AccountType.PASIVO, "nature": AccountNature.ACREEDORA, "level": 1},
    {"code": "21", "name": "PASIVO CORRIENTE", "type": AccountType.PASIVO, "nature": AccountNature.ACREEDORA, "level": 2, "parent": "2"},
    {"code": "2101", "name": "CUENTAS POR PAGAR COMERCIALES", "type": AccountType.PASIVO, "nature": AccountNature.ACREEDORA, "level": 3, "parent": "21", "credit": 12000.00},
    {"code": "2102", "name": "CUENTAS POR PAGAR NO COMERCIALES", "type": AccountType.PASIVO, "nature": AccountNature.ACREEDORA, "level": 3, "parent": "21", "credit": 8000.00},
    {"code": "2103", "name": "IMPUESTOS POR PAGAR", "type": AccountType.PASIVO, "nature": AccountNature.ACREEDORA, "level": 3, "parent": "21", "credit": 5000.00},
    {"code": "22", "name": "PASIVO NO CORRIENTE", "type": AccountType.PASIVO, "nature": AccountNature.ACREEDORA, "level": 2, "parent": "2"},
    {"code": "2201", "name": "OBLIGACIONES FINANCIERAS", "type": AccountType.PASIVO, "nature": AccountNature.ACREEDORA, "level": 3, "parent": "22", "credit": 50000.00},
    
    # PATRIMONIO
    {"code": "3", "name": "PATRIMONIO", "type": AccountType.PATRIMONIO, "nature": AccountNature.ACREEDORA, "level": 1},
    {"code": "31", "name": "CAPITAL", "type": AccountType.PATRIMONIO, "nature": AccountNature.ACREEDORA, "level": 2, "parent": "3"},
    {"code": "3101", "name": "CAPITAL SOCIAL", "type": AccountType.PATRIMONIO, "nature": AccountNature.ACREEDORA, "level": 3, "parent": "31", "credit": 100000.00},
    {"code": "3102", "name": "RESERVAS", "type": AccountType.PATRIMONIO, "nature": AccountNature.ACREEDORA, "level": 3, "parent": "31", "credit": 15000.00},
    {"code": "32", "name": "RESULTADOS", "type": AccountType.PATRIMONIO, "nature": AccountNature.ACREEDORA, "level": 2, "parent": "3"},
    {"code": "3201", "name": "UTILIDADES ACUMULADAS", "type": AccountType.PATRIMONIO, "nature": AccountNature.ACREEDORA, "level": 3, "parent": "32", "credit": 25000.00},
    
    # INGRESOS
    {"code": "4", "name": "INGRESOS", "type": AccountType.INGRESOS, "nature": AccountNature.ACREEDORA, "level": 1},
    {"code": "41", "name": "INGRESOS OPERACIONALES", "type": AccountType.INGRESOS, "nature": AccountNature.ACREEDORA, "level": 2, "parent": "4"},
    {"code": "4101", "name": "VENTAS", "type": AccountType.INGRESOS, "nature": AccountNature.ACREEDORA, "level": 3, "parent": "41"},
    {"code": "4102", "name": "SERVICIOS", "type": AccountType.INGRESOS, "nature": AccountNature.ACREEDORA, "level": 3, "parent": "41"},
    {"code": "42", "name": "INGRESOS NO OPERACIONALES", "type": AccountType.INGRESOS, "nature": AccountNature.ACREEDORA, "level": 2, "parent": "4"},
    {"code": "4201", "name": "INGRESOS FINANCIEROS", "type": AccountType.INGRESOS, "nature": AccountNature.ACREEDORA, "level": 3, "parent": "42"},
    
    # GASTOS
    {"code": "5", "name": "GASTOS", "type": AccountType.GASTOS, "nature": AccountNature.DEUDORA, "level": 1},
    {"code": "51", "name": "GASTOS OPERACIONALES", "type": AccountType.GASTOS, "nature": AccountNature.DEUDORA, "level": 2, "parent": "5"},
    {"code": "5101", "name": "GASTOS DE VENTAS", "type": AccountType.GASTOS, "nature": AccountNature.DEUDORA, "level": 3, "parent": "51"},
    {"code": "5102", "name": "GASTOS ADMINISTRATIVOS", "type": AccountType.GASTOS, "nature": AccountNature.DEUDORA, "level": 3, "parent": "51"},
    {"code": "52", "name": "GASTOS NO OPERACIONALES", "type": AccountType.GASTOS, "nature": AccountNature.DEUDORA, "level": 2, "parent": "5"},
    {"code": "5201", "name": "GASTOS FINANCIEROS", "type": AccountType.GASTOS, "nature": AccountNature.DEUDORA, "level": 3, "parent": "52"},
    
    # COSTOS
    {"code": "6", "name": "COSTOS", "type": AccountType.COSTOS, "nature": AccountNature.DEUDORA, "level": 1},
    {"code": "61", "name": "COSTO DE VENTAS", "type": AccountType.COSTOS, "nature": AccountNature.DEUDORA, "level": 2, "parent": "6"},
    {"code": "6101", "name": "COSTO DE MERCADERÍAS", "type": AccountType.COSTOS, "nature": AccountNature.DEUDORA, "level": 3, "parent": "61"},
    {"code": "62", "name": "COSTO DE PRODUCCIÓN", "type": AccountType.COSTOS, "nature": AccountNature.DEUDORA, "level": 2, "parent": "6"},
    {"code": "6201", "name": "MATERIA PRIMA CONSUMIDA", "type": AccountType.COSTOS, "nature": AccountNature.DEUDORA, "level": 3, "parent": "62"},
]

async def create_sample_chart():
    """Crear plan de cuentas de ejemplo"""
    
    # Conectar a la base de datos
    client = AsyncIOMotorClient(settings.mongodb_url)
    database = client[settings.database_name]
    
    await init_beanie(
        database=database,
        document_models=[User, Company, Account]
    )
    
    # Buscar una empresa existente o crear una de ejemplo
    company = await Company.find_one(Company.name == "Empresa de Ejemplo")
    if not company:
        print("No se encontró empresa de ejemplo. Creando una...")
        company = Company(
            name="Empresa de Ejemplo",
            ruc="1234567890001",
            legal_name="EMPRESA DE EJEMPLO S.A.",
            address="Av. Principal 123, Quito, Ecuador",
            phone="+593 2 1234567",
            email="ejemplo@empresa.com",
            created_by="system"
        )
        await company.insert()
        print(f"Empresa creada: {company.name}")
    
    # Buscar un usuario existente para asignar como creador
    user = await User.find_one()
    created_by = str(user.id) if user else "system"
    
    print(f"Creando plan de cuentas para empresa: {company.name}")
    
    created_count = 0
    for account_data in SAMPLE_CHART:
        # Verificar si la cuenta ya existe
        existing_account = await Account.find_one(
            Account.code == account_data["code"],
            Account.company_id == str(company.id)
        )
        
        if existing_account:
            print(f"Cuenta {account_data['code']} ya existe, actualizando saldos...")
            existing_account.initial_debit_balance = account_data.get("debit", 0.0)
            existing_account.initial_credit_balance = account_data.get("credit", 0.0)
            existing_account.current_debit_balance = account_data.get("debit", 0.0)
            existing_account.current_credit_balance = account_data.get("credit", 0.0)
            await existing_account.save()
            continue
        
        # Crear nueva cuenta
        account = Account(
            code=account_data["code"],
            name=account_data["name"],
            description=f"Cuenta {account_data['name']}",
            account_type=account_data["type"],
            nature=account_data["nature"],
            parent_code=account_data.get("parent"),
            level=account_data["level"],
            company_id=str(company.id),
            initial_debit_balance=account_data.get("debit", 0.0),
            initial_credit_balance=account_data.get("credit", 0.0),
            current_debit_balance=account_data.get("debit", 0.0),
            current_credit_balance=account_data.get("credit", 0.0),
            created_by=created_by
        )
        
        await account.insert()
        created_count += 1
        print(f"Cuenta creada: {account.code} - {account.name}")
    
    print(f"\n✅ Plan de cuentas creado exitosamente!")
    print(f"📊 Total de cuentas procesadas: {len(SAMPLE_CHART)}")
    print(f"🆕 Cuentas nuevas creadas: {created_count}")
    print(f"🏢 Empresa: {company.name}")
    
    # Calcular totales
    accounts = await Account.find(Account.company_id == str(company.id)).to_list()
    total_debit = sum(acc.initial_debit_balance for acc in accounts)
    total_credit = sum(acc.initial_credit_balance for acc in accounts)
    
    print(f"\n💰 Resumen de saldos:")
    print(f"   Total Débito: ${total_debit:,.2f}")
    print(f"   Total Crédito: ${total_credit:,.2f}")
    print(f"   Diferencia: ${abs(total_debit - total_credit):,.2f}")
    
    if abs(total_debit - total_credit) < 0.01:
        print("✅ El plan de cuentas está balanceado")
    else:
        print("⚠️  El plan de cuentas no está balanceado")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_sample_chart())
