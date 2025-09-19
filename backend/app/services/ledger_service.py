from typing import List, Optional
from datetime import datetime
from app.models.account import Account
from app.models.journal import JournalEntry, JournalLine
from app.models.ledger import LedgerEntry, LedgerEntryCreate, LedgerEntryType, AccountLedgerSummary
from app.models.ledger import LedgerEntryResponse as LedgerEntryResponseModel
from bson import ObjectId

class LedgerService:
    """Servicio para manejar el mayor general y mayorización de asientos"""
    
    @staticmethod
    async def post_journal_entry(journal_entry: JournalEntry, company_id: str, created_by: str) -> bool:
        """
        Mayorizar un asiento contable (aplicar las transacciones a las cuentas)
        """
        try:
            # Verificar que el asiento esté en estado DRAFT
            if journal_entry.status != "draft":
                raise ValueError("Solo se pueden mayorizar asientos en estado DRAFT")
            
            # Verificar si ya existen entradas del ledger para este asiento
            existing_entries = await LedgerEntry.find(
                LedgerEntry.journal_entry_id == str(journal_entry.id)
            ).to_list()
            
            if existing_entries:
                # Si ya existen entradas, actualizarlas en lugar de crear nuevas
                return await LedgerService._update_existing_ledger_entries(journal_entry, company_id, created_by)
            
            # Procesar cada línea del asiento
            affected_account_ids = set()
            for line in journal_entry.lines:
                # Buscar la cuenta
                account = await Account.find_one(
                    Account.code == line.account_code,
                    Account.company_id == company_id
                )
                
                if not account:
                    raise ValueError(f"Cuenta {line.account_code} no encontrada")
                
                # Crear entrada en el mayor
                ledger_entry = LedgerEntry(
                    account_id=str(account.id),
                    account_code=line.account_code,
                    account_name=line.account_name,
                    company_id=company_id,
                    entry_type=LedgerEntryType.JOURNAL,
                    journal_entry_id=str(journal_entry.id),
                    date=journal_entry.date,
                    description=line.description,
                    reference=line.reference or journal_entry.entry_number,
                    debit_amount=line.debit,
                    credit_amount=line.credit,
                    created_by=created_by
                )
                
                # Calcular saldos acumulados
                await LedgerService._calculate_running_balances(ledger_entry, account)
                
                # Guardar entrada en el mayor
                await ledger_entry.insert()
                
                # Actualizar saldos de la cuenta
                await LedgerService._update_account_balances(account, line.debit, line.credit)
                affected_account_ids.add(str(account.id))
            
            # Recalcular saldos acumulados para todas las cuentas afectadas
            for account_id in affected_account_ids:
                try:
                    acc = await Account.get(ObjectId(account_id))
                except Exception:
                    acc = await Account.find_one(Account.id == account_id)
                if acc:
                    await LedgerService._recalculate_running_balances(acc, company_id)

            # Calcular automáticamente saldos de cuentas padre
            print(f"🚀 EJECUTANDO cálculo automático de saldos padre post-mayorización...")
            await LedgerService._recalculate_parent_account_balances(affected_account_ids, company_id)
            print(f"🏁 FINALIZADO cálculo automático de saldos padre post-mayorización")

            # Marcar el asiento como POSTED
            journal_entry.status = "posted"
            journal_entry.updated_at = datetime.now()
            await journal_entry.save()
            
            return True
            
        except Exception as e:
            print(f"Error al mayorizar asiento: {e}")
            return False
    
    @staticmethod
    async def reverse_journal_entry(journal_entry: JournalEntry, company_id: str, created_by: str) -> bool:
        """
        Revertir un asiento contable (crear asiento de reversión)
        """
        try:
            # Crear asiento de reversión
            reversal_entry = JournalEntry(
                entry_number=f"REV-{journal_entry.entry_number}",
                date=datetime.now(),
                description=f"REVERSIÓN: {journal_entry.description}",
                entry_type=journal_entry.entry_type,
                status="draft",
                lines=[],
                total_debit=journal_entry.total_credit,  # Invertir totales
                total_credit=journal_entry.total_debit,
                company_id=company_id,
                created_by=created_by
            )
            
            # Crear líneas de reversión (invertir débitos y créditos)
            for line in journal_entry.lines:
                reversal_line = JournalLine(
                    account_code=line.account_code,
                    account_name=line.account_name,
                    description=f"REV: {line.description}",
                    debit=line.credit,  # Invertir
                    credit=line.debit,  # Invertir
                    reference=f"REV-{line.reference or ''}"
                )
                reversal_entry.lines.append(reversal_line)
            
            await reversal_entry.insert()
            
            # Mayorizar el asiento de reversión
            return await LedgerService.post_journal_entry(reversal_entry, company_id, created_by)
            
        except Exception as e:
            print(f"Error al revertir asiento: {e}")
            return False
    
    @staticmethod
    async def _calculate_running_balances(ledger_entry: LedgerEntry, account: Account):
        """
        Calcular saldos acumulados para una entrada del mayor
        """
        # Obtener la última entrada del mayor para esta cuenta
        last_entry = await LedgerEntry.find_one(
            LedgerEntry.account_id == str(account.id),
            sort=[("date", -1), ("created_at", -1)]
        )
        
        if last_entry:
            # Continuar desde el último saldo
            ledger_entry.running_debit_balance = last_entry.running_debit_balance + ledger_entry.debit_amount
            ledger_entry.running_credit_balance = last_entry.running_credit_balance + ledger_entry.credit_amount
        else:
            # Primera entrada, usar saldos iniciales
            ledger_entry.running_debit_balance = account.initial_debit_balance + ledger_entry.debit_amount
            ledger_entry.running_credit_balance = account.initial_credit_balance + ledger_entry.credit_amount
    
    @staticmethod
    async def _update_account_balances(account: Account, debit: float, credit: float):
        """
        Actualizar saldos actuales de una cuenta
        """
        account.current_debit_balance += debit
        account.current_credit_balance += credit
        account.last_transaction_date = datetime.now()
        account.updated_at = datetime.now()
        await account.save()
    
    @staticmethod
    async def _update_existing_ledger_entries(journal_entry: JournalEntry, company_id: str, created_by: str) -> bool:
        """
        Actualizar entradas existentes del ledger para un asiento
        """
        try:
            # Obtener entradas existentes
            existing_entries = await LedgerEntry.find(
                LedgerEntry.journal_entry_id == str(journal_entry.id)
            ).to_list()
            
            # Eliminar entradas existentes y revertir saldos de cuentas
            for entry in existing_entries:
                # Revertir saldos de la cuenta
                try:
                    account = await Account.get(ObjectId(entry.account_id))
                except:
                    # Si falla con ObjectId, intentar con string
                    account = await Account.find_one(Account.id == entry.account_id)
                
                if account:
                    account.current_debit_balance -= entry.debit_amount
                    account.current_credit_balance -= entry.credit_amount
                    await account.save()
                
                # Eliminar entrada del ledger
                await entry.delete()
            
            # Recalcular saldos acumulados para todas las cuentas afectadas
            affected_account_ids = set()
            for line in journal_entry.lines:
                account = await Account.find_one(
                    Account.code == line.account_code,
                    Account.company_id == company_id
                )
                if account:
                    affected_account_ids.add(str(account.id))
            
            # Recalcular saldos acumulados para cada cuenta afectada
            for account_id in affected_account_ids:
                try:
                    account = await Account.get(ObjectId(account_id))
                except:
                    account = await Account.find_one(Account.id == account_id)
                
                if account:
                    await LedgerService._recalculate_running_balances(account, company_id)

            # Recalcular saldos de cuentas padre
            await LedgerService._recalculate_parent_account_balances(affected_account_ids, company_id)
            
            # Crear nuevas entradas con los datos actualizados
            for line in journal_entry.lines:
                account = await Account.find_one(
                    Account.code == line.account_code,
                    Account.company_id == company_id
                )
                
                if not account:
                    raise ValueError(f"Cuenta {line.account_code} no encontrada")
                
                # Crear nueva entrada en el mayor
                ledger_entry = LedgerEntry(
                    account_id=str(account.id),
                    account_code=line.account_code,
                    account_name=line.account_name,
                    company_id=company_id,
                    entry_type=LedgerEntryType.JOURNAL,
                    journal_entry_id=str(journal_entry.id),
                    date=journal_entry.date,
                    description=line.description,
                    reference=line.reference or journal_entry.entry_number,
                    debit_amount=line.debit,
                    credit_amount=line.credit,
                    created_by=created_by
                )
                
                # Calcular saldos acumulados
                await LedgerService._calculate_running_balances(ledger_entry, account)
                
                # Guardar entrada en el mayor
                await ledger_entry.insert()
                
                # Actualizar saldos de la cuenta
                await LedgerService._update_account_balances(account, line.debit, line.credit)
            
            # Marcar el asiento como POSTED
            journal_entry.status = "posted"
            journal_entry.updated_at = datetime.now()
            await journal_entry.save()
            
            return True
            
        except Exception as e:
            print(f"Error al actualizar entradas del ledger: {e}")
            return False
    
    @staticmethod
    async def unpost_journal_entry(journal_entry: JournalEntry, company_id: str, created_by: str) -> bool:
        """
        Desmayorizar un asiento contable (eliminar entradas del ledger y revertir saldos)
        """
        try:
            # Verificar que el asiento esté en estado POSTED
            if journal_entry.status != "posted":
                raise ValueError("Solo se pueden desmayorizar asientos mayorizados")
            
            # Obtener entradas del ledger para este asiento
            ledger_entries = await LedgerEntry.find(
                LedgerEntry.journal_entry_id == str(journal_entry.id)
            ).to_list()
            
            # Revertir saldos de cuentas y eliminar entradas del ledger
            affected_account_ids = set()
            for entry in ledger_entries:
                # Revertir saldos de la cuenta
                try:
                    account = await Account.get(ObjectId(entry.account_id))
                except:
                    # Si falla con ObjectId, intentar con string
                    account = await Account.find_one(Account.id == entry.account_id)
                
                if account:
                    account.current_debit_balance -= entry.debit_amount
                    account.current_credit_balance -= entry.credit_amount
                    account.last_transaction_date = datetime.now()
                    account.updated_at = datetime.now()
                    await account.save()
                    affected_account_ids.add(str(account.id))
                
                # Eliminar entrada del ledger
                await entry.delete()
            
            # Recalcular saldos acumulados para todas las cuentas afectadas
            for account_id in affected_account_ids:
                try:
                    account = await Account.get(ObjectId(account_id))
                except:
                    account = await Account.find_one(Account.id == account_id)
                
                if account:
                    await LedgerService._recalculate_running_balances(account, company_id)

            # Recalcular saldos de cuentas padre después de desmayorizar
            await LedgerService._recalculate_parent_account_balances(affected_account_ids, company_id)
            
            # Cambiar estado del asiento a DRAFT
            journal_entry.status = "draft"
            journal_entry.updated_at = datetime.now()
            await journal_entry.save()
            
            return True
            
        except Exception as e:
            print(f"Error al desmayorizar asiento: {e}")
            return False
    
    @staticmethod
    async def _recalculate_running_balances(account: Account, company_id: str):
        """
        Recalcular saldos acumulados para una cuenta después de eliminar entradas
        """
        # Obtener todas las entradas del ledger para esta cuenta ordenadas por fecha
        ledger_entries = await LedgerEntry.find(
            LedgerEntry.account_id == str(account.id),
            LedgerEntry.company_id == company_id
        ).sort([("date", 1), ("created_at", 1)]).to_list()
        
        # Recalcular saldos acumulados
        running_debit = account.initial_debit_balance
        running_credit = account.initial_credit_balance
        
        for entry in ledger_entries:
            running_debit += entry.debit_amount
            running_credit += entry.credit_amount
            
            # Actualizar la entrada con los nuevos saldos acumulados
            entry.running_debit_balance = running_debit
            entry.running_credit_balance = running_credit
            await entry.save()
    
    @staticmethod
    async def get_account_ledger(account_id: str, company_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> AccountLedgerSummary:
        """
        Obtener el mayor de una cuenta específica
        """
        # Buscar la cuenta
        # Resolver la cuenta de manera robusta (string u ObjectId)
        account = None
        try:
            # Beanie suele aceptar string directamente; probamos primero
            account = await Account.get(account_id)
        except Exception:
            try:
                account = await Account.get(ObjectId(account_id))
            except Exception:
                try:
                    account = await Account.find_one(Account.id == ObjectId(account_id))
                except Exception:
                    account = None
        
        if not account:
            raise ValueError("Cuenta no encontrada")
        
        # Obtener entradas del mayor usando motor para evitar issues de tipos
        from motor.motor_asyncio import AsyncIOMotorClient
        from app.config import settings
        client = AsyncIOMotorClient(settings.mongodb_url)
        database = client[settings.database_name]
        collection = database.ledger_entries

        query = {
            "account_id": str(account.id),
            "company_id": company_id
        }
        if start_date:
            query["date"] = {"$gte": start_date}
        if end_date:
            from datetime import timedelta
            inclusive_end = end_date + timedelta(days=1)
            if "date" in query:
                query["date"]["$lt"] = inclusive_end
            else:
                query["date"] = {"$lt": inclusive_end}

        cursor = collection.find(query).sort("date", 1)
        raw_entries = await cursor.to_list(1000)
        client.close()
        
        # Calcular totales
        total_debits = sum(e.get("debit_amount", 0) for e in raw_entries)
        total_credits = sum(e.get("credit_amount", 0) for e in raw_entries)
        
        # Calcular saldo neto
        net_balance = account.current_debit_balance - account.current_credit_balance
        
        # Adaptar entradas al modelo esperado
        entry_models: list[LedgerEntryResponseModel] = []
        for e in raw_entries:
            entry_models.append(
                LedgerEntryResponseModel(
                    id=str(e.get("_id")),
                    account_id=e.get("account_id"),
                    account_code=e.get("account_code"),
                    account_name=e.get("account_name"),
                    company_id=e.get("company_id"),
                    entry_type=LedgerEntryType(e.get("entry_type")) if isinstance(e.get("entry_type"), str) else e.get("entry_type"),
                    journal_entry_id=e.get("journal_entry_id"),
                    date=e.get("date"),
                    description=e.get("description"),
                    reference=e.get("reference"),
                    debit_amount=e.get("debit_amount", 0),
                    credit_amount=e.get("credit_amount", 0),
                    running_debit_balance=e.get("running_debit_balance", 0),
                    running_credit_balance=e.get("running_credit_balance", 0),
                    created_at=e.get("created_at"),
                    created_by=e.get("created_by") or "",
                )
            )

        return AccountLedgerSummary(
            account_id=str(account.id),
            account_code=account.code,
            account_name=account.name,
            account_type=account.account_type.value,
            nature=account.nature.value,
            initial_debit_balance=account.initial_debit_balance,
            initial_credit_balance=account.initial_credit_balance,
            current_debit_balance=account.current_debit_balance,
            current_credit_balance=account.current_credit_balance,
            net_balance=net_balance,
            total_debits=total_debits,
            total_credits=total_credits,
            entry_count=len(entry_models),
            last_transaction_date=account.last_transaction_date,
            entries=entry_models
        )
    
    @staticmethod
    async def get_general_ledger(company_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[AccountLedgerSummary]:
        """
        Obtener el mayor general de todas las cuentas
        """
        print(f"🔍 Buscando cuentas para empresa: {company_id}")

        # Obtener todas las cuentas activas de la empresa
        accounts = await Account.find(
            Account.company_id == company_id,
            Account.is_active == True
        ).to_list()

        print(f"📊 Cuentas encontradas: {len(accounts)}")

        # Obtener todas las entradas del ledger para la empresa
        from motor.motor_asyncio import AsyncIOMotorClient
        from app.config import settings
        
        client = AsyncIOMotorClient(settings.mongodb_url)
        database = client[settings.database_name]
        collection = database.ledger_entries
        
        # Construir query para MongoDB
        query = {"company_id": company_id}
        if start_date:
            query["date"] = {"$gte": start_date}
        if end_date:
            from datetime import timedelta
            inclusive_end = end_date + timedelta(days=1)
            if "date" in query:
                query["date"]["$lt"] = inclusive_end
            else:
                query["date"] = {"$lt": inclusive_end}
        
        # Obtener todas las entradas del ledger
        ledger_entries = await collection.find(query).sort("date", 1).to_list(1000)
        print(f"📊 Entradas del ledger encontradas: {len(ledger_entries)}")
        
        # Agrupar entradas por account_id
        entries_by_account = {}
        for entry in ledger_entries:
            account_id = entry["account_id"]
            if account_id not in entries_by_account:
                entries_by_account[account_id] = []
            entries_by_account[account_id].append(entry)
        
        client.close()

        # Crear resumen del mayor para cada cuenta
        ledgers = []
        for account in accounts:
            try:
                account_id = str(account.id)
                entries = entries_by_account.get(account_id, [])
                
                print(f"🔍 Procesando cuenta: {account.code} - {account.name}")
                print(f"   Entradas encontradas: {len(entries)}")
                
                # Calcular totales
                total_debits = sum(entry["debit_amount"] for entry in entries)
                total_credits = sum(entry["credit_amount"] for entry in entries)
                
                # Calcular saldo neto
                net_balance = account.current_debit_balance - account.current_credit_balance
                
                # Crear resumen del mayor
                ledger_summary = AccountLedgerSummary(
                    account_id=str(account.id),
                    account_code=account.code,
                    account_name=account.name,
                    account_type=account.account_type.value,
                    nature=account.nature.value,
                    initial_debit_balance=account.initial_debit_balance,
                    initial_credit_balance=account.initial_credit_balance,
                    current_debit_balance=account.current_debit_balance,
                    current_credit_balance=account.current_credit_balance,
                    net_balance=net_balance,
                    total_debits=total_debits,
                    total_credits=total_credits,
                    entry_count=len(entries),
                    last_transaction_date=account.last_transaction_date,
                    entries=[]
                )
                
                ledgers.append(ledger_summary)
                
            except Exception as e:
                print(f"Error al obtener mayor de cuenta {account.code}: {e}")
                continue

        return ledgers

    @staticmethod
    async def _recalculate_parent_account_balances(affected_account_ids: set, company_id: str):
        """
        Recalcular automáticamente los saldos de todas las cuentas padre en la jerarquía
        cuando se mayoriza un asiento que afecta a cuentas hijas
        """
        try:
            print(f"🔄 INICIANDO recálculo automático de saldos padre para {len(affected_account_ids)} cuentas afectadas")
            print(f"🔍 Cuentas afectadas: {affected_account_ids}")
            
            # Usar exactamente el mismo método que el endpoint manual
            result = await LedgerService._fix_complete_hierarchy_internal(company_id)
            print(f"🎯 COMPLETADO: Jerarquía completa corregida automáticamente")
            print(f"📊 Resultado: {result['updated_count']} cuentas padre actualizadas")
            
            # Mostrar detalles de las correcciones realizadas
            if result.get('corrections'):
                for correction in result['corrections'][:5]:  # Mostrar solo las primeras 5
                    print(f"✅ {correction['parent_code']} ({correction['parent_name']}): {correction['old_balance']} → {correction['new_balance']}")
                
        except Exception as e:
            print(f"❌ ERROR al recalcular saldos de cuentas padre: {e}")
            import traceback
            print(f"📋 Traceback completo: {traceback.format_exc()}")
            
            # En caso de error, intentar corrección completa como fallback
            try:
                print("🔄 Intentando corrección completa como fallback...")
                await LedgerService._fix_complete_hierarchy_fallback(company_id)
                print("✅ Corrección de fallback completada")
            except Exception as fallback_error:
                print(f"❌ Error en corrección de fallback: {fallback_error}")
                print(f"📋 Fallback traceback: {traceback.format_exc()}")
    
    @staticmethod
    async def _fix_complete_hierarchy_internal(company_id: str):
        """
        Método interno para corregir completamente toda la jerarquía de saldos padre
        (Usado tanto por el endpoint manual como por el cálculo automático)
        """
        # Obtener todas las cuentas activas de la empresa
        all_accounts = await Account.find(
            Account.company_id == company_id,
            Account.is_active == True
        ).to_list()
        
        print(f"🔍 INICIANDO corrección de jerarquía completa para {len(all_accounts)} cuentas")
        print(f"📋 Códigos de cuentas encontradas: {[acc.code for acc in all_accounts[:10]]}...")  # Mostrar solo las primeras 10
        
        # Crear mapa de cuentas por código
        accounts_by_code = {acc.code: acc for acc in all_accounts}
        
        # Identificar todas las cuentas padre
        parent_accounts = []
        for account in all_accounts:
            # Verificar si tiene cuentas hijas
            has_children = any(
                acc.parent_code == account.code or 
                (acc.code.startswith(account.code) and acc.code != account.code and len(acc.code) > len(account.code))
                for acc in all_accounts
            )
            if has_children:
                parent_accounts.append(account)
                print(f"🔍 Cuenta padre identificada: {account.code} ({account.name})")
        
        print(f"📊 Encontradas {len(parent_accounts)} cuentas padre")
        
        # Ordenar por longitud de código (más específico primero)
        parent_accounts.sort(key=lambda x: len(x.code), reverse=True)
        
        # Recalcular saldos para cada cuenta padre
        updated_count = 0
        corrections = []
        
        for parent_account in parent_accounts:
            # Calcular saldo basándose en hijas
            children = []
            
            # Buscar por parent_code directo
            for account in all_accounts:
                if account.parent_code == parent_account.code:
                    children.append(account)
            
            # Buscar por jerarquía de códigos
            for account in all_accounts:
                if (account.code.startswith(parent_account.code) and 
                    account.code != parent_account.code and 
                    account not in children):
                    
                    # Verificar si es hija directa
                    is_direct_child = False
                    
                    # Lógica mejorada para identificar hijas directas
                    if len(parent_account.code) == 1:
                        # Padre de 1 dígito -> hijas de 3 dígitos
                        if len(account.code) == 3:
                            is_direct_child = True
                    elif len(parent_account.code) == 3:
                        # Padre de 3 dígitos -> hijas de 5 dígitos
                        if len(account.code) == 5:
                            is_direct_child = True
                    elif len(parent_account.code) == 5:
                        # Padre de 5 dígitos -> hijas de 7 dígitos
                        if len(account.code) == 7:
                            is_direct_child = True
                    elif len(parent_account.code) == 7:
                        # Padre de 7 dígitos -> hijas de 9 dígitos
                        if len(account.code) == 9:
                            is_direct_child = True
                    else:
                        # Lógica genérica: hija directa si tiene exactamente 2 dígitos más
                        if len(account.code) == len(parent_account.code) + 2:
                            is_direct_child = True
                    
                    if is_direct_child:
                        children.append(account)
                        print(f"   👶 Hija directa encontrada: {account.code} ({account.name}) para padre {parent_account.code}")
            
            # Calcular saldos totales
            total_debit = sum(child.current_debit_balance for child in children)
            total_credit = sum(child.current_credit_balance for child in children)
            
            old_debit = parent_account.current_debit_balance
            old_credit = parent_account.current_credit_balance
            
            print(f"   💰 Cálculo de saldos para {parent_account.code}:")
            print(f"      📊 Hijas encontradas: {len(children)}")
            for child in children:
                print(f"         - {child.code}: D={child.current_debit_balance}, C={child.current_credit_balance}")
            print(f"      🧮 Total calculado: D={total_debit}, C={total_credit}")
            print(f"      📈 Saldo anterior: D={old_debit}, C={old_credit}")
            
            # Actualizar saldos
            parent_account.current_debit_balance = total_debit
            parent_account.current_credit_balance = total_credit
            parent_account.last_transaction_date = datetime.now()
            parent_account.updated_at = datetime.now()
            
            await parent_account.save()
            print(f"      ✅ Saldo actualizado y guardado en BD")
            
            corrections.append({
                "parent_code": parent_account.code,
                "parent_name": parent_account.name,
                "children_count": len(children),
                "old_balance": f"D:{old_debit}, C:{old_credit}",
                "new_balance": f"D:{total_debit}, C:{total_credit}",
                "children": [{"code": child.code, "name": child.name, "balance": f"D:{child.current_debit_balance}, C:{child.current_credit_balance}"} for child in children]
            })
            
            updated_count += 1
            
            print(f"✅ CORREGIDO {parent_account.code} ({parent_account.name}): D={old_debit}→{total_debit}, C={old_credit}→{total_credit}")
            print(f"   📊 Hijas incluidas ({len(children)}): {[child.code for child in children]}")
        
        return {
            "updated_count": updated_count,
            "corrections": corrections
        }
    
    @staticmethod
    async def _calculate_parent_balance(parent_account: Account, all_accounts: List[Account]):
        """
        Calcular el saldo de una cuenta padre basándose en sus cuentas hijas
        """
        try:
            print(f"   🔍 Calculando saldo para cuenta padre: {parent_account.code} - {parent_account.name}")
            
            # Encontrar todas las cuentas hijas de esta cuenta padre
            children = []
            
            # Buscar por parent_code directo
            for account in all_accounts:
                if account.parent_code == parent_account.code:
                    children.append(account)
                    print(f"      📋 Hija encontrada por parent_code: {account.code} - {account.name}")
            
            # También buscar por jerarquía de códigos (cuentas que empiecen con el código del padre)
            # Incluir todas las cuentas hijas directas (nivel inmediatamente siguiente)
            for account in all_accounts:
                if (account.code.startswith(parent_account.code) and 
                    account.code != parent_account.code and 
                    account not in children):
                    
                    # Verificar si es hija directa
                    # Lógica mejorada para diferentes niveles de jerarquía
                    is_direct_child = False
                    
                    # Caso 1: Código padre de 1 dígito (ej: "1") -> buscar códigos de 3 dígitos (ej: "101", "102")
                    if len(parent_account.code) == 1:
                        if len(account.code) == 3:
                            is_direct_child = True
                    
                    # Caso 2: Código padre de 3 dígitos (ej: "101") -> buscar códigos de 5 dígitos (ej: "10101", "10102")
                    elif len(parent_account.code) == 3:
                        if len(account.code) == 5:
                            is_direct_child = True
                    
                    # Caso 3: Código padre de 5 dígitos (ej: "10101") -> buscar códigos de 7 dígitos (ej: "1010101", "1010102")
                    elif len(parent_account.code) == 5:
                        if len(account.code) == 7:
                            is_direct_child = True
                    
                    # Caso 4: Código padre de 7 dígitos (ej: "1010101") -> buscar códigos de 9 dígitos (ej: "101010101", "101010102")
                    elif len(parent_account.code) == 7:
                        if len(account.code) == 9:
                            is_direct_child = True
                    
                    # Caso general: si el código es exactamente 2 dígitos más largo
                    else:
                        if len(account.code) == len(parent_account.code) + 2:
                            is_direct_child = True
                    
                    if is_direct_child:
                        children.append(account)
                        print(f"      📋 Hija encontrada por jerarquía: {account.code} - {account.name}")
            
            print(f"   📋 Total cuentas hijas encontradas para {parent_account.code}: {len(children)}")
            
            # Calcular saldos totales de las cuentas hijas
            total_debit = 0.0
            total_credit = 0.0
            
            for child in children:
                total_debit += child.current_debit_balance
                total_credit += child.current_credit_balance
                print(f"      - {child.code} ({child.name}): D={child.current_debit_balance}, C={child.current_credit_balance}")
            
            # Actualizar saldos de la cuenta padre
            old_debit = parent_account.current_debit_balance
            old_credit = parent_account.current_credit_balance
            
            parent_account.current_debit_balance = total_debit
            parent_account.current_credit_balance = total_credit
            parent_account.last_transaction_date = datetime.now()
            parent_account.updated_at = datetime.now()
            
            await parent_account.save()
            
            print(f"   💰 Saldo actualizado para {parent_account.code}: D={old_debit}→{total_debit}, C={old_credit}→{total_credit}")
            
        except Exception as e:
            print(f"❌ Error al calcular saldo de cuenta padre {parent_account.code}: {e}")
    
    @staticmethod
    async def _fix_complete_hierarchy_fallback(company_id: str):
        """
        Método de fallback para corregir toda la jerarquía en caso de error
        """
        try:
            print("🔄 Ejecutando corrección completa de jerarquía como fallback...")
            
            # Obtener todas las cuentas activas de la empresa
            all_accounts = await Account.find(
                Account.company_id == company_id,
                Account.is_active == True
            ).to_list()
            
            # Identificar todas las cuentas padre
            parent_accounts = []
            for account in all_accounts:
                # Verificar si tiene cuentas hijas
                has_children = any(
                    acc.parent_code == account.code or 
                    (acc.code.startswith(account.code) and acc.code != account.code and len(acc.code) > len(account.code))
                    for acc in all_accounts
                )
                if has_children:
                    parent_accounts.append(account)
            
            print(f"📊 Encontradas {len(parent_accounts)} cuentas padre para corrección de fallback")
            
            # Ordenar por longitud de código (más específico primero)
            parent_accounts.sort(key=lambda x: len(x.code), reverse=True)
            
            # Recalcular saldos para cada cuenta padre
            for parent_account in parent_accounts:
                await LedgerService._calculate_parent_balance(parent_account, all_accounts)
                print(f"✅ Fallback: Actualizado saldo de cuenta padre: {parent_account.code} - {parent_account.name}")
                
        except Exception as e:
            print(f"❌ Error en corrección de fallback: {e}")



