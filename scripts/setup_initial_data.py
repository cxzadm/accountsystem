#!/usr/bin/env python3
"""
Script de configuración inicial del sistema contable
Permite configurar datos iniciales, crear usuarios admin y importar backups
"""

import os
import sys
import json
import asyncio
import getpass
from pathlib import Path
from datetime import datetime

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from motor.motor_asyncio import AsyncIOMotorClient
    from app.config import settings
    from app.models.user import User, UserRole, UserStatus
    from app.models.company import Company, CompanyStatus
    from app.models.account import Account, AccountType, AccountNature
    from app.models.document_type import DocumentType
    from app.auth.jwt_handler import create_access_token
    import bcrypt
except ImportError:
    print("❌ Error: No se pudo importar las dependencias del proyecto")
    print("   Asegúrate de estar en el directorio correcto y tener las dependencias instaladas")
    sys.exit(1)

class InitialSetup:
    def __init__(self, mongodb_url: str, database_name: str):
        self.mongodb_url = mongodb_url
        self.database_name = database_name
        self.client = None
        self.db = None
    
    async def connect(self):
        """Conectar a la base de datos"""
        try:
            self.client = AsyncIOMotorClient(self.mongodb_url)
            self.db = self.client[self.database_name]
            await self.client.admin.command('ping')
            print("✅ Conexión a MongoDB establecida")
            return True
        except Exception as e:
            print(f"❌ Error conectando a MongoDB: {e}")
            return False
    
    async def close(self):
        """Cerrar conexión"""
        if self.client:
            self.client.close()
    
    async def check_system_status(self):
        """Verificar estado del sistema"""
        print("\n🔍 Verificando estado del sistema...")
        
        # Verificar usuarios
        users_count = await self.db.users.count_documents({})
        print(f"   👥 Usuarios: {users_count}")
        
        # Verificar empresas
        companies_count = await self.db.companies.count_documents({})
        print(f"   🏢 Empresas: {companies_count}")
        
        # Verificar cuentas
        accounts_count = await self.db.accounts.count_documents({})
        print(f"   📊 Cuentas contables: {accounts_count}")
        
        # Verificar asientos
        journal_count = await self.db.journal_entries.count_documents({})
        print(f"   📝 Asientos contables: {journal_count}")
        
        return {
            "users": users_count,
            "companies": companies_count,
            "accounts": accounts_count,
            "journal_entries": journal_count
        }
    
    async def create_admin_user(self):
        """Crear usuario administrador inicial"""
        print("\n👤 Configurando usuario administrador...")
        
        # Verificar si ya existe un admin
        existing_admin = await self.db.users.find_one({"role": "admin"})
        if existing_admin:
            print("⚠️  Ya existe un usuario administrador en el sistema")
            return existing_admin
        
        # Solicitar datos del administrador
        print("Ingresa los datos del usuario administrador:")
        username = input("Usuario: ").strip()
        email = input("Email: ").strip()
        first_name = input("Nombre: ").strip()
        last_name = input("Apellido: ").strip()
        
        while True:
            password = getpass.getpass("Contraseña: ")
            if len(password) < 6:
                print("❌ La contraseña debe tener al menos 6 caracteres")
                continue
            
            confirm_password = getpass.getpass("Confirmar contraseña: ")
            if password != confirm_password:
                print("❌ Las contraseñas no coinciden")
                continue
            break
        
        # Crear hash de la contraseña
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Crear usuario
        admin_user = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "first_name": first_name,
            "last_name": last_name,
            "role": "admin",
            "status": "active",
            "permissions": ["*"],  # Todos los permisos
            "companies": [],
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "created_by": "system"
        }
        
        result = await self.db.users.insert_one(admin_user)
        admin_user["_id"] = result.inserted_id
        
        print(f"✅ Usuario administrador creado: {username}")
        return admin_user
    
    async def create_sample_company(self):
        """Crear empresa de ejemplo"""
        print("\n🏢 Creando empresa de ejemplo...")
        
        # Verificar si ya existen empresas
        existing_companies = await self.db.companies.count_documents({})
        if existing_companies > 0:
            print("⚠️  Ya existen empresas en el sistema")
            return None
        
        # Datos de la empresa de ejemplo
        company_data = {
            "name": "Empresa de Ejemplo S.A.",
            "ruc": "1234567890001",
            "legal_name": "EMPRESA DE EJEMPLO SOCIEDAD ANÓNIMA",
            "address": "Av. Principal 123, Quito, Ecuador",
            "phone": "+593-2-1234567",
            "email": "info@empresa-ejemplo.com",
            "status": "active",
            "fiscal_year_start": 1,
            "currency": "USD",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "created_by": "system"
        }
        
        result = await self.db.companies.insert_one(company_data)
        company_data["_id"] = result.inserted_id
        
        print(f"✅ Empresa creada: {company_data['name']}")
        return company_data
    
    async def create_basic_chart_of_accounts(self, company_id: str):
        """Crear plan de cuentas básico"""
        print("\n📊 Creando plan de cuentas básico...")
        
        # Plan de cuentas básico para Ecuador
        basic_accounts = [
            # ACTIVOS
            {"code": "1", "name": "ACTIVOS", "account_type": "activo", "nature": "deudora", "level": 1},
            {"code": "11", "name": "ACTIVO CORRIENTE", "account_type": "activo", "nature": "deudora", "level": 2, "parent_code": "1"},
            {"code": "1101", "name": "CAJA Y BANCOS", "account_type": "activo", "nature": "deudora", "level": 3, "parent_code": "11"},
            {"code": "110101", "name": "Caja", "account_type": "activo", "nature": "deudora", "level": 4, "parent_code": "1101"},
            {"code": "110102", "name": "Bancos", "account_type": "activo", "nature": "deudora", "level": 4, "parent_code": "1101"},
            
            # PASIVOS
            {"code": "2", "name": "PASIVOS", "account_type": "pasivo", "nature": "acreedora", "level": 1},
            {"code": "21", "name": "PASIVO CORRIENTE", "account_type": "pasivo", "nature": "acreedora", "level": 2, "parent_code": "2"},
            {"code": "2101", "name": "OBLIGACIONES FINANCIERAS", "account_type": "pasivo", "nature": "acreedora", "level": 3, "parent_code": "21"},
            
            # PATRIMONIO
            {"code": "3", "name": "PATRIMONIO", "account_type": "patrimonio", "nature": "acreedora", "level": 1},
            {"code": "31", "name": "CAPITAL", "account_type": "patrimonio", "nature": "acreedora", "level": 2, "parent_code": "3"},
            {"code": "3101", "name": "CAPITAL SOCIAL", "account_type": "patrimonio", "nature": "acreedora", "level": 3, "parent_code": "31"},
            
            # INGRESOS
            {"code": "4", "name": "INGRESOS", "account_type": "ingresos", "nature": "acreedora", "level": 1},
            {"code": "41", "name": "INGRESOS DE EXPLOTACIÓN", "account_type": "ingresos", "nature": "acreedora", "level": 2, "parent_code": "4"},
            {"code": "4101", "name": "VENTAS", "account_type": "ingresos", "nature": "acreedora", "level": 3, "parent_code": "41"},
            
            # GASTOS
            {"code": "5", "name": "GASTOS", "account_type": "gastos", "nature": "deudora", "level": 1},
            {"code": "51", "name": "GASTOS DE EXPLOTACIÓN", "account_type": "gastos", "nature": "deudora", "level": 2, "parent_code": "5"},
            {"code": "5101", "name": "GASTOS ADMINISTRATIVOS", "account_type": "gastos", "nature": "deudora", "level": 3, "parent_code": "51"},
        ]
        
        # Crear cuentas
        accounts_created = 0
        for account_data in basic_accounts:
            account = {
                **account_data,
                "company_id": company_id,
                "is_active": True,
                "is_editable": True,
                "initial_debit_balance": 0.0,
                "initial_credit_balance": 0.0,
                "current_debit_balance": 0.0,
                "current_credit_balance": 0.0,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "created_by": "system"
            }
            
            await self.db.accounts.insert_one(account)
            accounts_created += 1
        
        print(f"✅ Plan de cuentas básico creado: {accounts_created} cuentas")
        return accounts_created
    
    async def create_basic_document_types(self, company_id: str):
        """Crear tipos de documentos básicos"""
        print("\n📄 Creando tipos de documentos básicos...")
        
        # Tipos de documentos básicos
        document_types = [
            {
                "code": "CE",
                "name": "COMPROBANTE DE EGRESO",
                "is_electronic": False,
                "next_sequence": 0,
                "padding": 5,
                "company_id": company_id,
                "is_active": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "created_by": "system"
            },
            {
                "code": "CI",
                "name": "COMPROBANTE DE INGRESO",
                "is_electronic": False,
                "next_sequence": 0,
                "padding": 5,
                "company_id": company_id,
                "is_active": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "created_by": "system"
            },
            {
                "code": "AS",
                "name": "ASIENTO CONTABLE",
                "is_electronic": False,
                "next_sequence": 0,
                "padding": 6,
                "company_id": company_id,
                "is_active": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "created_by": "system"
            }
        ]
        
        # Crear tipos de documento
        for doc_type in document_types:
            await self.db.document_types.insert_one(doc_type)
        
        print(f"✅ Tipos de documentos creados: {len(document_types)}")
        return len(document_types)
    
    async def import_backup_file(self, backup_file: str):
        """Importar archivo de backup"""
        print(f"\n📥 Importando archivo de backup: {backup_file}")
        
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Determinar estructura
            if "metadata" in data and "data" in data:
                collections_data = data["data"]
            else:
                collections_data = data
            
            # Importar cada colección
            total_imported = 0
            for collection_name, documents in collections_data.items():
                if isinstance(documents, list) and documents:
                    # Limpiar colección existente
                    await self.db[collection_name].delete_many({})
                    
                    # Insertar documentos
                    await self.db[collection_name].insert_many(documents)
                    total_imported += len(documents)
                    print(f"   ✅ {collection_name}: {len(documents)} documentos")
            
            print(f"✅ Backup importado: {total_imported} documentos")
            return True
            
        except Exception as e:
            print(f"❌ Error importando backup: {e}")
            return False

async def main():
    """Función principal"""
    print("🏦 Sistema Contable Ecuador - Configuración Inicial")
    print("=" * 60)
    
    # Configuración de conexión
    mongodb_url = settings.mongodb_url
    database_name = settings.database_name
    
    print(f"🔗 MongoDB: {mongodb_url}")
    print(f"🗄️  Base de datos: {database_name}")
    
    # Crear setup
    setup = InitialSetup(mongodb_url, database_name)
    
    try:
        # Conectar
        if not await setup.connect():
            return 1
        
        # Verificar estado del sistema
        status = await setup.check_system_status()
        
        # Menú de opciones
        print("\n📋 Opciones de configuración:")
        print("1. Configuración completa (usuario admin + empresa + plan de cuentas)")
        print("2. Solo crear usuario administrador")
        print("3. Solo crear empresa de ejemplo")
        print("4. Importar archivo de backup")
        print("5. Ver estado del sistema")
        
        choice = input("\nSelecciona una opción (1-5): ").strip()
        
        if choice == "1":
            # Configuración completa
            await setup.create_admin_user()
            company = await setup.create_sample_company()
            if company:
                await setup.create_basic_chart_of_accounts(str(company["_id"]))
                await setup.create_basic_document_types(str(company["_id"]))
            print("\n✅ Configuración completa finalizada")
            
        elif choice == "2":
            # Solo usuario admin
            await setup.create_admin_user()
            print("\n✅ Usuario administrador creado")
            
        elif choice == "3":
            # Solo empresa
            company = await setup.create_sample_company()
            if company:
                await setup.create_basic_chart_of_accounts(str(company["_id"]))
                await setup.create_basic_document_types(str(company["_id"]))
            print("\n✅ Empresa de ejemplo creada")
            
        elif choice == "4":
            # Importar backup
            backup_file = input("Ruta al archivo de backup: ").strip()
            if os.path.exists(backup_file):
                await setup.import_backup_file(backup_file)
            else:
                print(f"❌ Archivo no encontrado: {backup_file}")
            
        elif choice == "5":
            # Ver estado
            print("\n📊 Estado actual del sistema:")
            print(f"   👥 Usuarios: {status['users']}")
            print(f"   🏢 Empresas: {status['companies']}")
            print(f"   📊 Cuentas: {status['accounts']}")
            print(f"   📝 Asientos: {status['journal_entries']}")
            
        else:
            print("❌ Opción inválida")
            return 1
        
        print("\n🎉 ¡Configuración completada exitosamente!")
        print("🚀 El sistema está listo para usar")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n👋 Operación cancelada por el usuario")
        return 0
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return 1
    finally:
        await setup.close()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)


