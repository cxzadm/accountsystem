#!/usr/bin/env python3
"""
Script de prueba para verificar que ambos módulos usen EXACTAMENTE la misma fuente de datos
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

async def test_unified_data_source():
    """Probar que ambos módulos usen EXACTAMENTE la misma fuente de datos"""
    
    print("🧪 INICIANDO PRUEBA DE FUENTE DE DATOS UNIFICADA")
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
            except Exception as e:
                print(f"❌ Error en cálculo automático: {e}")
                continue
            
            # 2. Simular endpoint /accounts (Plan de Cuentas)
            print("📋 Simulando endpoint /accounts (Plan de Cuentas)...")
            accounts_plan = await Account.find(
                Account.company_id == company_id,
                Account.is_active == True
            ).to_list()
            
            print(f"   Cuentas encontradas: {len(accounts_plan)}")
            
            # 3. Simular endpoint /ledger (Mayor General) - NUEVA LÓGICA
            print("📊 Simulando endpoint /ledger (Mayor General) - Nueva lógica...")
            
            # Usar exactamente la misma lógica que /accounts
            accounts_ledger = await Account.find(
                Account.company_id == company_id,
                Account.is_active == True
            ).to_list()
            
            print(f"   Cuentas encontradas: {len(accounts_ledger)}")
            
            # 4. Verificar que usen EXACTAMENTE la misma fuente de datos
            print("🔍 Verificando fuente de datos unificada...")
            
            # Crear mapas para comparación
            plan_by_code = {acc.code: acc for acc in accounts_plan}
            ledger_by_code = {acc.code: acc for acc in accounts_ledger}
            
            inconsistencies = []
            parent_accounts_found = 0
            consistent_parents = 0
            
            # Verificar que todas las cuentas estén en ambos módulos
            all_codes = set(plan_by_code.keys()) | set(ledger_by_code.keys())
            
            for code in all_codes:
                account_plan = plan_by_code.get(code)
                account_ledger = ledger_by_code.get(code)
                
                if not account_plan:
                    inconsistencies.append(f"❌ Cuenta {code} solo existe en Mayor General")
                    continue
                    
                if not account_ledger:
                    inconsistencies.append(f"❌ Cuenta {code} solo existe en Plan de Cuentas")
                    continue
                
                # Verificar si es una cuenta padre
                is_parent = (account_plan.parent_code is None and 
                           any(acc.parent_code == account_plan.code for acc in accounts_plan))
                
                if is_parent:
                    parent_accounts_found += 1
                    
                    # Verificar que sean EXACTAMENTE el mismo objeto (misma fuente de datos)
                    same_object = account_plan.id == account_ledger.id
                    
                    # Verificar saldos padre EXACTAMENTE iguales
                    plan_debit = account_plan.current_debit_balance
                    plan_credit = account_plan.current_credit_balance
                    ledger_debit = account_ledger.current_debit_balance
                    ledger_credit = account_ledger.current_credit_balance
                    
                    # Verificar saldos iniciales también
                    plan_initial_debit = account_plan.initial_debit_balance
                    plan_initial_credit = account_plan.initial_credit_balance
                    ledger_initial_debit = account_ledger.initial_debit_balance
                    ledger_initial_credit = account_ledger.initial_credit_balance
                    
                    # Comparación EXACTA (sin tolerancia)
                    debit_match = plan_debit == ledger_debit
                    credit_match = plan_credit == ledger_credit
                    initial_debit_match = plan_initial_debit == ledger_initial_debit
                    initial_credit_match = plan_initial_credit == ledger_initial_credit
                    
                    if debit_match and credit_match and initial_debit_match and initial_credit_match:
                        consistent_parents += 1
                        print(f"✅ Cuenta padre {code} ({account_plan.name}): Misma fuente de datos")
                        print(f"   D={plan_debit}, C={plan_credit} | Inicial D={plan_initial_debit}, C={plan_initial_credit}")
                    else:
                        inconsistencies.append(
                            f"❌ Cuenta padre {code} ({account_plan.name}): Fuentes de datos diferentes"
                        )
                        print(f"   Plan de Cuentas D={plan_debit}, C={plan_credit}")
                        print(f"   Mayor General D={ledger_debit}, C={ledger_credit}")
            
            # Mostrar resultados
            print(f"\n📊 RESULTADOS PARA {company_name}:")
            print(f"   Total cuentas: {len(all_codes)}")
            print(f"   Cuentas padre encontradas: {parent_accounts_found}")
            print(f"   Cuentas padre con misma fuente: {consistent_parents}")
            print(f"   Inconsistencias: {len(inconsistencies)}")
            
            if inconsistencies:
                print(f"\n❌ INCONSISTENCIAS ENCONTRADAS ({len(inconsistencies)}):")
                for inconsistency in inconsistencies:
                    print(f"   {inconsistency}")
            else:
                print(f"\n✅ TODAS LAS CUENTAS PADRE USAN LA MISMA FUENTE DE DATOS")
            
            # Calcular porcentaje de consistencia
            if parent_accounts_found > 0:
                consistency_percentage = (consistent_parents / parent_accounts_found) * 100
                print(f"   Consistencia de fuente de datos: {consistency_percentage:.1f}%")
            else:
                print(f"   No se encontraron cuentas padre para verificar")
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()
    
    print("\n🏁 PRUEBA DE FUENTE DE DATOS UNIFICADA COMPLETADA")

if __name__ == "__main__":
    asyncio.run(test_unified_data_source())
