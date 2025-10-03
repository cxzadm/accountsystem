#!/usr/bin/env python3
"""
Script de prueba para verificar el endpoint de importación de base de datos
"""

import requests
import json
import os
from pathlib import Path

def test_database_endpoints():
    """Probar los endpoints de base de datos"""
    
    # Configuración
    base_url = "http://localhost:8005"
    test_user = {
        "username": "admin",
        "password": "admin123"
    }
    
    print("🧪 Iniciando pruebas de endpoints de base de datos...")
    
    # 1. Autenticación
    print("\n1️⃣ Probando autenticación...")
    try:
        auth_response = requests.post(f"{base_url}/api/auth/login", json=test_user)
        if auth_response.status_code == 200:
            token = auth_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Autenticación exitosa")
        else:
            print(f"❌ Error en autenticación: {auth_response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return
    
    # 2. Probar endpoint de prueba
    print("\n2️⃣ Probando endpoint de prueba...")
    try:
        test_response = requests.get(f"{base_url}/api/database/test", headers=headers)
        if test_response.status_code == 200:
            print("✅ Endpoint de prueba funcionando")
            print(f"   Respuesta: {test_response.json()}")
        else:
            print(f"❌ Error en endpoint de prueba: {test_response.status_code}")
            print(f"   Respuesta: {test_response.text}")
    except Exception as e:
        print(f"❌ Error en endpoint de prueba: {e}")
    
    # 3. Probar endpoint de estado
    print("\n3️⃣ Probando endpoint de estado...")
    try:
        status_response = requests.get(f"{base_url}/api/database/status", headers=headers)
        if status_response.status_code == 200:
            print("✅ Endpoint de estado funcionando")
            status_data = status_response.json()
            print(f"   Estado: {status_data.get('success', False)}")
            print(f"   Mensaje: {status_data.get('message', 'N/A')}")
        else:
            print(f"❌ Error en endpoint de estado: {status_response.status_code}")
            print(f"   Respuesta: {status_response.text}")
    except Exception as e:
        print(f"❌ Error en endpoint de estado: {e}")
    
    # 4. Crear archivo de prueba para importación
    print("\n4️⃣ Creando archivo de prueba...")
    test_data = {
        "metadata": {
            "export_date": "2025-01-30T10:00:00Z",
            "version": "1.0",
            "database": "sistema_contable_ec"
        },
        "data": {
            "test_collection": [
                {"_id": "test1", "name": "Test Document 1", "value": 100},
                {"_id": "test2", "name": "Test Document 2", "value": 200}
            ]
        }
    }
    
    test_file_path = "test_import.json"
    try:
        with open(test_file_path, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2)
        print(f"✅ Archivo de prueba creado: {test_file_path}")
    except Exception as e:
        print(f"❌ Error creando archivo de prueba: {e}")
        return
    
    # 5. Probar importación
    print("\n5️⃣ Probando importación...")
    try:
        # Configuración de base de datos
        db_config = {
            "HOST": "localhost",
            "PORT": 27017,
            "DATABASE": "sistema_contable_ec",
            "USERNAME": "",
            "PASSWORD": ""
        }
        
        # Preparar datos para envío
        files = {'file': open(test_file_path, 'rb')}
        data = {
            'config': json.dumps(db_config),
            'mode': 'replace'
        }
        
        import_response = requests.post(
            f"{base_url}/api/database/import",
            files=files,
            data=data,
            headers=headers
        )
        
        files['file'].close()  # Cerrar archivo
        
        if import_response.status_code == 200:
            print("✅ Importación exitosa")
            import_data = import_response.json()
            print(f"   Documentos importados: {import_data.get('imported', 0)}")
            print(f"   Colecciones procesadas: {import_data.get('collections_processed', 0)}")
        else:
            print(f"❌ Error en importación: {import_response.status_code}")
            print(f"   Respuesta: {import_response.text}")
            
    except Exception as e:
        print(f"❌ Error en importación: {e}")
    
    # 6. Limpiar archivo de prueba
    try:
        os.remove(test_file_path)
        print(f"\n🧹 Archivo de prueba eliminado: {test_file_path}")
    except:
        pass
    
    print("\n🎉 Pruebas completadas!")

if __name__ == "__main__":
    test_database_endpoints()
