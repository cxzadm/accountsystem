#!/usr/bin/env python3
"""
Script de prueba para verificar la consistencia de saldos padre
entre el Plan de Cuentas y el Mayor General
"""

import asyncio
import sys
import os
from datetime import datetime

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.account import Account
from app.services.ledger_service import LedgerService
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

async def test_consistency():
    """Probar la consistencia entre Plan de Cuentas y Mayor General"""
    
    print("🧪 INICIANDO PRUEBA DE CONSISTENCIA DE SALDOS PADRE")
    print("=" * 60)
    
    # Conectar a MongoDB
    client = AsyncIOMotorClient(settings.mongodb_url)
    database = client[settings.database_name]
    
    try:
        # Obtener todas las empresas
        companies_collection = database.companies
        companies = await companies_collection.find({}).to_list(100)
        
        if not companies:
            print("❌ No se encontraron empresas en la base de datos")
            return
        
        print(f"📊 Empresas encontradas: {len(companies)}")
        
        for company in companies:
            company_id = str(company['_id'])
            company_name = company.get('name', 'Sin nombre')
            
            print(f"\n🏢 PROBANDO EMPRESA: {company_name} (ID: {company_id})")
            print("-" * 50)
            
            # 1. Obtener cuentas del Plan de Cuentas (endpoint /accounts)
            print("📋 Obteniendo datos del Plan de Cuentas...")
            accounts = await Account.find(
                Account.company_id == company_id,
                Account.is_active == True
            ).to_list()
            
            print(f"   Cuentas encontradas: {len(accounts)}")
            
            # 2. Obtener datos del Mayor General (endpoint /ledger)
            print("📊 Obteniendo datos del Mayor General...")
            ledgers = await LedgerService.get_general_ledger(company_id)
            
            print(f"   Cuentas en mayor general: {len(ledgers)}")
            
            # 3. Verificar consistencia
            print("🔍 Verificando consistencia...")
            
            # Crear mapas para comparación
            accounts_by_code = {acc.code: acc for acc in accounts}
            ledgers_by_code = {ledger.account_code: ledger for ledger in ledgers}
            
            inconsistencies = []
            
            # Verificar que todas las cuentas estén en ambos módulos
            all_codes = set(accounts_by_code.keys()) | set(ledgers_by_code.keys())
            
            for code in all_codes:
                account = accounts_by_code.get(code)
                ledger = ledgers_by_code.get(code)
                
                if not account:
                    inconsistencies.append(f"❌ Cuenta {code} solo existe en Mayor General")
                    continue
                    
                if not ledger:
                    inconsistencies.append(f"❌ Cuenta {code} solo existe en Plan de Cuentas")
                    continue
                
                # Verificar saldos padre
                if account.parent_code or any(acc.parent_code == account.code for acc in accounts):
                    # Es una cuenta padre, verificar consistencia de saldos
                    account_debit = account.current_debit_balance
                    account_credit = account.current_credit_balance
                    ledger_debit = ledger.current_debit_balance
                    ledger_credit = ledger.current_credit_balance
                    
                    if abs(account_debit - ledger_debit) > 0.01 or abs(account_credit - ledger_credit) > 0.01:
                        inconsistencies.append(
                            f"❌ Cuenta padre {code} ({account.name}): "
                            f"Plan de Cuentas D={account_debit}, C={account_credit} | "
                            f"Mayor General D={ledger_debit}, C={ledger_credit}"
                        )
                    else:
                        print(f"✅ Cuenta padre {code} ({account.name}): Saldos consistentes")
            
            # Mostrar resultados
            if inconsistencies:
                print(f"\n❌ INCONSISTENCIAS ENCONTRADAS ({len(inconsistencies)}):")
                for inconsistency in inconsistencies:
                    print(f"   {inconsistency}")
            else:
                print(f"\n✅ TODAS LAS CUENTAS SON CONSISTENTES")
            
            print(f"\n📊 RESUMEN PARA {company_name}:")
            print(f"   Total cuentas: {len(all_codes)}")
            print(f"   Inconsistencias: {len(inconsistencies)}")
            print(f"   Consistencia: {((len(all_codes) - len(inconsistencies)) / len(all_codes) * 100):.1f}%")
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()
    
    print("\n🏁 PRUEBA DE CONSISTENCIA COMPLETADA")

if __name__ == "__main__":
    asyncio.run(test_consistency())
