#!/usr/bin/env python3
"""
Script para importar datos iniciales al sistema contable
Permite seleccionar un archivo de backup JSON para importar en la primera configuración
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from motor.motor_asyncio import AsyncIOMotorClient
    from app.config import settings
except ImportError:
    print("❌ Error: No se pudo importar las dependencias del proyecto")
    print("   Asegúrate de estar en el directorio correcto y tener las dependencias instaladas")
    sys.exit(1)

class DatabaseImporter:
    def __init__(self, mongodb_url: str, database_name: str):
        self.mongodb_url = mongodb_url
        self.database_name = database_name
        self.client = None
        self.db = None
    
    async def connect(self):
        """Conectar a la base de datos MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.mongodb_url)
            self.db = self.client[self.database_name]
            
            # Verificar conexión
            await self.client.admin.command('ping')
            print("✅ Conexión a MongoDB establecida correctamente")
            return True
        except Exception as e:
            print(f"❌ Error conectando a MongoDB: {e}")
            return False
    
    async def close(self):
        """Cerrar conexión a la base de datos"""
        if self.client:
            self.client.close()
    
    async def check_existing_data(self) -> bool:
        """Verificar si ya existen datos en la base de datos"""
        try:
            collections = await self.db.list_collection_names()
            total_docs = 0
            
            for collection_name in collections:
                count = await self.db[collection_name].count_documents({})
                total_docs += count
                if count > 0:
                    print(f"   📊 {collection_name}: {count} documentos")
            
            if total_docs > 0:
                print(f"⚠️  La base de datos ya contiene {total_docs} documentos en {len(collections)} colecciones")
                return True
            else:
                print("✅ La base de datos está vacía, lista para importar datos iniciales")
                return False
        except Exception as e:
            print(f"❌ Error verificando datos existentes: {e}")
            return True
    
    def select_backup_file(self, backup_dir: str = None) -> Optional[str]:
        """Seleccionar archivo de backup para importar"""
        if not backup_dir:
            # Buscar en directorios comunes
            possible_dirs = [
                ".",
                "backups",
                "data",
                "exports",
                os.path.expanduser("~/Downloads"),
                os.path.expanduser("~/Desktop")
            ]
            
            for dir_path in possible_dirs:
                if os.path.exists(dir_path):
                    backup_dir = dir_path
                    break
        
        if not os.path.exists(backup_dir):
            print(f"❌ Directorio no encontrado: {backup_dir}")
            return None
        
        # Buscar archivos JSON de backup
        json_files = []
        for file in os.listdir(backup_dir):
            if file.endswith('.json') and ('backup' in file.lower() or 'sistema_contable' in file.lower()):
                file_path = os.path.join(backup_dir, file)
                file_size = os.path.getsize(file_path)
                json_files.append((file, file_path, file_size))
        
        if not json_files:
            print(f"❌ No se encontraron archivos de backup JSON en: {backup_dir}")
            print("   Buscando archivos que contengan 'backup' o 'sistema_contable' en el nombre")
            return None
        
        # Ordenar por tamaño (archivos más grandes primero)
        json_files.sort(key=lambda x: x[2], reverse=True)
        
        print(f"\n📁 Archivos de backup encontrados en {backup_dir}:")
        print("=" * 60)
        
        for i, (filename, filepath, size) in enumerate(json_files, 1):
            size_mb = size / (1024 * 1024)
            print(f"{i:2d}. {filename}")
            print(f"    📏 Tamaño: {size_mb:.2f} MB")
            print(f"    📍 Ruta: {filepath}")
            print()
        
        while True:
            try:
                choice = input(f"Selecciona un archivo (1-{len(json_files)}) o 'q' para salir: ").strip()
                
                if choice.lower() == 'q':
                    return None
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(json_files):
                    selected_file = json_files[choice_num - 1][1]
                    print(f"✅ Archivo seleccionado: {os.path.basename(selected_file)}")
                    return selected_file
                else:
                    print(f"❌ Opción inválida. Debe ser un número entre 1 y {len(json_files)}")
            except ValueError:
                print("❌ Entrada inválida. Ingresa un número o 'q' para salir")
            except KeyboardInterrupt:
                print("\n👋 Operación cancelada por el usuario")
                return None
    
    def validate_backup_file(self, file_path: str) -> Dict:
        """Validar estructura del archivo de backup"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print("🔍 Validando estructura del archivo de backup...")
            
            # Verificar estructura básica
            if not isinstance(data, dict):
                raise ValueError("El archivo debe contener un objeto JSON")
            
            # Verificar si tiene metadata (formato de backup completo)
            if "metadata" in data and "data" in data:
                print("✅ Formato de backup completo detectado")
                collections = list(data["data"].keys())
                metadata = data["metadata"]
                
                print(f"   📊 Base de datos: {metadata.get('database', 'N/A')}")
                print(f"   📅 Fecha de backup: {metadata.get('backup_date', 'N/A')}")
                print(f"   👤 Creado por: {metadata.get('created_by', 'N/A')}")
                print(f"   📋 Colecciones: {len(collections)}")
                
                for collection in collections:
                    doc_count = len(data["data"][collection])
                    print(f"      - {collection}: {doc_count} documentos")
                
                return {
                    "valid": True,
                    "type": "complete_backup",
                    "collections": collections,
                    "metadata": metadata,
                    "data": data["data"]
                }
            
            # Verificar si es un objeto con colecciones directas
            elif any(key in data for key in ['accounts', 'companies', 'users', 'journal_entries']):
                print("✅ Formato de datos directos detectado")
                collections = list(data.keys())
                
                print(f"   📋 Colecciones encontradas: {len(collections)}")
                for collection in collections:
                    if isinstance(data[collection], list):
                        doc_count = len(data[collection])
                        print(f"      - {collection}: {doc_count} documentos")
                    else:
                        print(f"      - {collection}: (no es una lista)")
                
                return {
                    "valid": True,
                    "type": "direct_data",
                    "collections": collections,
                    "data": data
                }
            
            else:
                raise ValueError("Estructura de archivo no reconocida")
                
        except json.JSONDecodeError as e:
            print(f"❌ Error parseando JSON: {e}")
            return {"valid": False, "error": "Archivo JSON inválido"}
        except Exception as e:
            print(f"❌ Error validando archivo: {e}")
            return {"valid": False, "error": str(e)}
    
    async def import_data(self, file_path: str, mode: str = "replace") -> bool:
        """Importar datos a la base de datos"""
        try:
            # Validar archivo
            validation = self.validate_backup_file(file_path)
            if not validation["valid"]:
                print(f"❌ Archivo inválido: {validation.get('error', 'Error desconocido')}")
                return False
            
            print(f"\n🚀 Iniciando importación en modo '{mode}'...")
            
            imported_count = 0
            collections_processed = 0
            
            for collection_name, documents in validation["data"].items():
                if not isinstance(documents, list):
                    print(f"⚠️  Saltando {collection_name}: no es una lista de documentos")
                    continue
                
                print(f"📥 Procesando {collection_name}...")
                
                # Obtener colección
                collection = self.db[collection_name]
                
                if mode == "replace":
                    # Eliminar documentos existentes
                    result = await collection.delete_many({})
                    if result.deleted_count > 0:
                        print(f"   🗑️  Eliminados {result.deleted_count} documentos existentes")
                
                if documents:
                    # Insertar documentos
                    if mode == "upsert":
                        # Upsert: actualizar si existe, insertar si no
                        for doc in documents:
                            if '_id' in doc:
                                await collection.replace_one(
                                    {"_id": doc['_id']}, 
                                    doc, 
                                    upsert=True
                                )
                            else:
                                await collection.insert_one(doc)
                            imported_count += 1
                    else:
                        # Insertar normalmente
                        await collection.insert_many(documents)
                        imported_count += len(documents)
                    
                    print(f"   ✅ Importados {len(documents)} documentos")
                else:
                    print(f"   ⚠️  Colección vacía, saltando...")
                
                collections_processed += 1
            
            print(f"\n🎉 Importación completada exitosamente!")
            print(f"   📊 Colecciones procesadas: {collections_processed}")
            print(f"   📄 Documentos importados: {imported_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error durante la importación: {e}")
            return False

async def main():
    """Función principal del script"""
    parser = argparse.ArgumentParser(description="Importar datos iniciales al sistema contable")
    parser.add_argument("--file", "-f", help="Ruta al archivo de backup JSON")
    parser.add_argument("--dir", "-d", help="Directorio donde buscar archivos de backup")
    parser.add_argument("--mode", "-m", choices=["insert", "upsert", "replace"], 
                       default="replace", help="Modo de importación (default: replace)")
    parser.add_argument("--force", action="store_true", 
                       help="Forzar importación aunque ya existan datos")
    parser.add_argument("--mongodb-url", help="URL de conexión a MongoDB")
    parser.add_argument("--database", help="Nombre de la base de datos")
    
    args = parser.parse_args()
    
    print("🏦 Sistema Contable Ecuador - Importador de Datos Iniciales")
    print("=" * 60)
    
    # Configurar conexión a la base de datos
    mongodb_url = args.mongodb_url or settings.mongodb_url
    database_name = args.database or settings.database_name
    
    print(f"🔗 Conectando a: {mongodb_url}")
    print(f"🗄️  Base de datos: {database_name}")
    
    # Crear importador
    importer = DatabaseImporter(mongodb_url, database_name)
    
    try:
        # Conectar a la base de datos
        if not await importer.connect():
            return 1
        
        # Verificar datos existentes
        has_data = await importer.check_existing_data()
        if has_data and not args.force:
            print("\n⚠️  La base de datos ya contiene datos.")
            response = input("¿Deseas continuar de todos modos? (s/N): ").strip().lower()
            if response not in ['s', 'si', 'sí', 'y', 'yes']:
                print("👋 Operación cancelada")
                return 0
        
        # Seleccionar archivo
        if args.file:
            file_path = args.file
            if not os.path.exists(file_path):
                print(f"❌ Archivo no encontrado: {file_path}")
                return 1
            print(f"📁 Usando archivo especificado: {file_path}")
        else:
            file_path = importer.select_backup_file(args.dir)
            if not file_path:
                print("👋 No se seleccionó ningún archivo")
                return 0
        
        # Importar datos
        success = await importer.import_data(file_path, args.mode)
        
        if success:
            print("\n✅ ¡Importación completada exitosamente!")
            print("🚀 El sistema está listo para usar")
            return 0
        else:
            print("\n❌ La importación falló")
            return 1
            
    except KeyboardInterrupt:
        print("\n👋 Operación cancelada por el usuario")
        return 0
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return 1
    finally:
        await importer.close()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)


