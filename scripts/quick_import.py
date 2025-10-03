#!/usr/bin/env python3
"""
Script rápido para importar datos iniciales
Versión simplificada del importador para casos de uso básicos
"""

import os
import sys
import json
import asyncio
from pathlib import Path

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from motor.motor_asyncio import AsyncIOMotorClient
    from app.config import settings
except ImportError:
    print("❌ Error: No se pudo importar las dependencias del proyecto")
    sys.exit(1)

async def quick_import(backup_file: str, mongodb_url: str = None, database_name: str = None):
    """Importación rápida de datos"""
    
    # Configuración por defecto
    mongodb_url = mongodb_url or settings.mongodb_url
    database_name = database_name or settings.database_name
    
    print(f"🚀 Importación rápida iniciada...")
    print(f"📁 Archivo: {backup_file}")
    print(f"🔗 MongoDB: {mongodb_url}")
    print(f"🗄️  Base de datos: {database_name}")
    
    try:
        # Conectar a MongoDB
        client = AsyncIOMotorClient(mongodb_url)
        db = client[database_name]
        
        # Verificar conexión
        await client.admin.command('ping')
        print("✅ Conexión establecida")
        
        # Cargar archivo JSON
        with open(backup_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Determinar estructura del archivo
        if "metadata" in data and "data" in data:
            # Formato de backup completo
            collections_data = data["data"]
            print("📊 Formato de backup completo detectado")
        else:
            # Formato directo
            collections_data = data
            print("📊 Formato directo detectado")
        
        # Importar cada colección
        total_imported = 0
        for collection_name, documents in collections_data.items():
            if isinstance(documents, list) and documents:
                # Limpiar colección existente
                await db[collection_name].delete_many({})
                
                # Insertar documentos
                await db[collection_name].insert_many(documents)
                total_imported += len(documents)
                print(f"✅ {collection_name}: {len(documents)} documentos")
        
        print(f"\n🎉 Importación completada: {total_imported} documentos importados")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        client.close()
    
    return True

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python quick_import.py <archivo_backup.json>")
        print("Ejemplo: python quick_import.py backup_sistema_contable_2025-09-30.json")
        sys.exit(1)
    
    backup_file = sys.argv[1]
    
    if not os.path.exists(backup_file):
        print(f"❌ Archivo no encontrado: {backup_file}")
        sys.exit(1)
    
    print("🏦 Sistema Contable Ecuador - Importación Rápida")
    print("=" * 50)
    
    # Ejecutar importación
    success = asyncio.run(quick_import(backup_file))
    
    if success:
        print("✅ ¡Importación exitosa!")
        sys.exit(0)
    else:
        print("❌ Importación falló")
        sys.exit(1)

if __name__ == "__main__":
    main()


