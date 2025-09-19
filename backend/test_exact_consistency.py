#!/usr/bin/env python3
"""
Script de prueba para verificar que los saldos padre sean EXACTAMENTE iguales
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

async def test_exact_consistency():
    """Probar que los saldos padre sean EXACTAMENTE iguales entre módulos"""
    
    print("🧪 INICIANDO PRUEBA DE CONSISTENCIA EXACTA DE SALDOS PADRE")
    print("=" * 70)
    
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
            print("-" * 60)
            
            # 1. Ejecutar cálculo automático de saldos padre (misma lógica que ambos módulos)
            print("🔄 Ejecutando cálculo automático de saldos padre...")
            try:
                result = await LedgerService._fix_complete_hierarchy_internal(company_id)
                print(f"✅ Cálculo completado: {result['updated_count']} cuentas padre actualizadas")
                
                if result['corrections']:
                    print("📋 Correcciones realizadas:")
                    for correction in result['corrections'][:5]:  # Mostrar solo las primeras 5
                        print(f"   - {correction['parent_code']}: {correction['old_balance']} → {correction['new_balance']}")
                    if len(result['corrections']) > 5:
                        print(f"   ... y {len(result['corrections']) - 5} más")
                        
            except Exception as e:
                print(f"❌ Error en cálculo automático: {e}")
                continue
            
            # 2. Obtener cuentas del Plan de Cuentas (endpoint /accounts)
            print("📋 Obteniendo datos del Plan de Cuentas...")
            accounts = await Account.find(
                Account.company_id == company_id,
                Account.is_active == True
            ).to_list()
            
            print(f"   Cuentas encontradas: {len(accounts)}")
            
            # 3. Obtener datos del Mayor General (endpoint /ledger)
            print("📊 Obteniendo datos del Mayor General...")
            ledgers = await LedgerService.get_general_ledger(company_id)
            
            print(f"   Cuentas en mayor general: {len(ledgers)}")
            
            # 4. Verificar consistencia EXACTA
            print("🔍 Verificando consistencia EXACTA...")
            
            # Crear mapas para comparación
            accounts_by_code = {acc.code: acc for acc in accounts}
            ledgers_by_code = {ledger.account_code: ledger for ledger in ledgers}
            
            inconsistencies = []
            parent_accounts_found = 0
            consistent_parents = 0
            
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
                
                # Verificar si es una cuenta padre
                is_parent = (account.parent_code is None and 
                           any(acc.parent_code == account.code for acc in accounts))
                
                if is_parent:
                    parent_accounts_found += 1
                    
                    # Verificar saldos padre EXACTAMENTE iguales
                    account_debit = account.current_debit_balance
                    account_credit = account.current_credit_balance
                    ledger_debit = ledger.current_debit_balance
                    ledger_credit = ledger.current_credit_balance
                    
                    # Verificar saldos iniciales también
                    account_initial_debit = account.initial_debit_balance
                    account_initial_credit = account.initial_credit_balance
                    ledger_initial_debit = ledger.initial_debit_balance
                    ledger_initial_credit = ledger.initial_credit_balance
                    
                    # Comparación EXACTA (sin tolerancia)
                    debit_match = account_debit == ledger_debit
                    credit_match = account_credit == ledger_credit
                    initial_debit_match = account_initial_debit == ledger_initial_debit
                    initial_credit_match = account_initial_credit == ledger_initial_credit
                    
                    if debit_match and credit_match and initial_debit_match and initial_credit_match:
                        consistent_parents += 1
                        print(f"✅ Cuenta padre {code} ({account.name}): Saldos EXACTAMENTE iguales")
                        print(f"   D={account_debit}, C={account_credit} | Inicial D={account_initial_debit}, C={account_initial_credit}")
                    else:
                        inconsistencies.append(
                            f"❌ Cuenta padre {code} ({account.name}): "
                            f"Plan de Cuentas D={account_debit}, C={account_credit} | "
                            f"Mayor General D={ledger_debit}, C={ledger_credit} | "
                            f"Inicial Plan D={account_initial_debit}, C={account_initial_credit} | "
                            f"Inicial Mayor D={ledger_initial_debit}, C={ledger_initial_credit}"
                        )
            
            # Mostrar resultados
            print(f"\n📊 RESULTADOS PARA {company_name}:")
            print(f"   Total cuentas: {len(all_codes)}")
            print(f"   Cuentas padre encontradas: {parent_accounts_found}")
            print(f"   Cuentas padre consistentes: {consistent_parents}")
            print(f"   Inconsistencias: {len(inconsistencies)}")
            
            if inconsistencies:
                print(f"\n❌ INCONSISTENCIAS ENCONTRADAS ({len(inconsistencies)}):")
                for inconsistency in inconsistencies:
                    print(f"   {inconsistency}")
            else:
                print(f"\n✅ TODAS LAS CUENTAS PADRE SON EXACTAMENTE CONSISTENTES")
            
            # Calcular porcentaje de consistencia
            if parent_accounts_found > 0:
                consistency_percentage = (consistent_parents / parent_accounts_found) * 100
                print(f"   Consistencia de saldos padre: {consistency_percentage:.1f}%")
            else:
                print(f"   No se encontraron cuentas padre para verificar")
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()
    
    print("\n🏁 PRUEBA DE CONSISTENCIA EXACTA COMPLETADA")

if __name__ == "__main__":
    asyncio.run(test_exact_consistency())
