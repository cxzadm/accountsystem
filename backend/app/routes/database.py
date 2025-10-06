from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import List, Optional
from app.models.user import User
from app.auth.dependencies import get_current_user, require_permission, log_audit, AuditAction, AuditModule
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from app.config import settings
import json
import csv
import io
import os
import subprocess
import tempfile
from datetime import datetime
import asyncio

router = APIRouter()

def process_document_for_import(doc):
    """
    Procesa un documento para importación, validando y convirtiendo ObjectIds correctamente
    """
    try:
        processed_doc = doc.copy()
        
        # Procesar el campo _id si existe
        if '_id' in processed_doc:
            _id = processed_doc['_id']
            
            # Si es un string, intentar convertirlo a ObjectId
            if isinstance(_id, str):
                try:
                    processed_doc['_id'] = ObjectId(_id)
                except Exception as e:
                    print(f"   ⚠️  Error convirtiendo _id '{_id}' a ObjectId: {e}")
                    # Si no se puede convertir, usar el string como está
                    pass
            # Si ya es un ObjectId, mantenerlo
            elif isinstance(_id, ObjectId):
                pass
            # Si es un dict (ObjectId serializado), intentar reconstruirlo
            elif isinstance(_id, dict) and '$oid' in _id:
                try:
                    processed_doc['_id'] = ObjectId(_id['$oid'])
                except Exception as e:
                    print(f"   ⚠️  Error reconstruyendo ObjectId desde dict: {e}")
                    return None
        
        # Procesar otros campos que puedan contener ObjectIds
        for key, value in processed_doc.items():
            if key != '_id' and isinstance(value, str) and len(value) == 24:
                # Verificar si parece un ObjectId (24 caracteres hexadecimales)
                try:
                    if all(c in '0123456789abcdefABCDEF' for c in value):
                        processed_doc[key] = ObjectId(value)
                except:
                    pass  # Si no es un ObjectId válido, mantener como string
        
        return processed_doc
        
    except Exception as e:
        print(f"   ❌ Error procesando documento: {e}")
        return None

async def get_unique_query_for_collection(collection_name, doc):
    """
    Obtiene una consulta única para verificar duplicados según el tipo de colección
    """
    try:
        # Definir campos únicos por colección
        unique_fields = {
            'users': ['username', 'email'],
            'companies': ['ruc', 'name'],
            'accounts': ['account_code', 'company'],
            'journal_entries': ['entry_number', 'company'],
            'document_types': ['abbreviation', 'company'],
        }
        
        fields_to_check = unique_fields.get(collection_name, ['name', 'code'])
        
        # Construir consulta con campos únicos disponibles en el documento
        query = {}
        for field in fields_to_check:
            if field in doc:
                query[field] = doc[field]
                break  # Usar el primer campo único encontrado
        
        return query
        
    except Exception as e:
        print(f"   ⚠️  Error construyendo consulta única: {e}")
        return {}

async def verify_import_integrity(db, collection_name, expected_count):
    """
    Verifica la integridad de los datos después de la importación
    """
    try:
        collection = db[collection_name]
        actual_count = await collection.count_documents({})
        
        print(f"   🔍 Verificación de integridad para {collection_name}:")
        print(f"   📊 Documentos esperados: {expected_count}")
        print(f"   📊 Documentos encontrados: {actual_count}")
        
        if actual_count == expected_count:
            print(f"   ✅ Integridad verificada correctamente")
            return True
        else:
            print(f"   ⚠️  Advertencia: conteo de documentos no coincide")
            return False
            
    except Exception as e:
        print(f"   ❌ Error verificando integridad: {e}")
        return False

@router.get("/test")
async def test_database_endpoint(current_user: User = Depends(get_current_user)):
    """Endpoint de prueba para verificar que el servidor esté funcionando"""
    return {
        "success": True,
        "message": "Endpoint de base de datos funcionando correctamente",
        "user": current_user.username,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/status")
async def get_database_status(
    host: str = "localhost",
    port: int = 27017,
    database: str = "sistema_contable_ec",
    username: Optional[str] = None,
    password: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Verificar el estado de la base de datos"""
    try:
        # Construir URI de conexión
        if username and password:
            uri = f"mongodb://{username}:{password}@{host}:{port}/{database}"
        else:
            uri = f"mongodb://{host}:{port}/{database}"
        
        # Conectar a MongoDB
        client = AsyncIOMotorClient(uri)
        
        # Verificar conexión
        await client.admin.command('ping')
        
        # Obtener información de la base de datos
        db = client[database]
        collections = await db.list_collection_names()
        
        # Contar documentos en cada colección
        total_documents = 0
        collection_info = []
        
        for collection_name in collections:
            count = await db[collection_name].count_documents({})
            total_documents += count
            collection_info.append({
                "name": collection_name,
                "count": count
            })
        
        client.close()
        
        return {
            "success": True,
            "message": "Conexión exitosa a la base de datos",
            "info": {
                "host": host,
                "port": port,
                "database": database,
                "collections": len(collections),
                "documents": total_documents,
                "collection_details": collection_info
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error de conexión: {str(e)}",
            "info": None
        }

@router.post("/export")
async def export_database(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Exportar la base de datos usando mongoexport"""
    try:
        # Obtener parámetros del body de la request
        body = await request.json()
        host = body.get("HOST", "localhost")
        port = body.get("PORT", 27017)
        database = body.get("DATABASE", "sistema_contable_ec")
        username = body.get("USERNAME")
        password = body.get("PASSWORD")
        format = body.get("format", "json")
        collections = body.get("collections", ["all"])
        
        # Construir URI de conexión
        if username and password:
            uri = f"mongodb://{username}:{password}@{host}:{port}/{database}"
        else:
            uri = f"mongodb://{host}:{port}/{database}"
        
        # Verificar conexión
        client = AsyncIOMotorClient(uri)
        await client.admin.command('ping')
        db = client[database]
        
        # Obtener colecciones a exportar
        if "all" in collections:
            collection_names = await db.list_collection_names()
        else:
            collection_names = collections
        
        # Crear archivo temporal
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_dir = tempfile.mkdtemp()
        
        if format == "json":
            # Exportar como JSON
            export_data = {}
            
            for collection_name in collection_names:
                collection = db[collection_name]
                documents = await collection.find({}).to_list(None)
                export_data[collection_name] = documents
            
            # Crear archivo JSON
            json_content = json.dumps(export_data, indent=2, default=str)
            
            # Crear respuesta de streaming
            def generate():
                yield json_content.encode('utf-8')
            
            return StreamingResponse(
                generate(),
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename=backup_sistema_contable_{timestamp}.json"
                }
            )
            
        elif format == "csv":
            # Exportar como CSV (solo la primera colección para CSV)
            if collection_names:
                collection_name = collection_names[0]
                collection = db[collection_name]
                documents = await collection.find({}).to_list(None)
                
                if documents:
                    # Obtener todas las claves únicas
                    all_keys = set()
                    for doc in documents:
                        all_keys.update(doc.keys())
                    
                    # Crear CSV
                    output = io.StringIO()
                    writer = csv.DictWriter(output, fieldnames=sorted(all_keys))
                    writer.writeheader()
                    
                    for doc in documents:
                        # Convertir ObjectId a string
                        for key, value in doc.items():
                            if hasattr(value, '__str__'):
                                doc[key] = str(value)
                        writer.writerow(doc)
                    
                    csv_content = output.getvalue()
                    output.close()
                    
                    # Crear respuesta de streaming
                    def generate():
                        yield csv_content.encode('utf-8')
                    
                    return StreamingResponse(
                        generate(),
                        media_type="text/csv",
                        headers={
                            "Content-Disposition": f"attachment; filename=backup_{collection_name}_{timestamp}.csv"
                        }
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="No hay documentos en la colección"
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No se especificaron colecciones para exportar"
                )
        
        client.close()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al exportar la base de datos: {str(e)}"
        )

@router.post("/import")
async def import_database(
    file: UploadFile = File(...),
    config: str = Form(...),
    mode: str = Form("insert"),
    current_user: User = Depends(get_current_user)
):
    """Importar datos a la base de datos usando mongoimport"""
    try:
        print(f"🚀 Iniciando importación de archivo: {file.filename}")
        print(f"📋 Modo: {mode}")
        print(f"👤 Usuario: {current_user.username}")
        
        # Parsear configuración
        try:
            db_config = json.loads(config)
            print(f"🔧 Configuración de BD: {db_config}")
        except json.JSONDecodeError as e:
            print(f"❌ Error parseando configuración: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Configuración JSON inválida"
            )
        
        # Usar configuración por defecto si no se proporciona
        host = db_config.get('HOST', 'localhost')
        port = db_config.get('PORT', 27017)
        database = db_config.get('DATABASE', 'sistema_contable_ec')
        username = db_config.get('USERNAME')
        password = db_config.get('PASSWORD')
        
        # Construir URI de conexión
        if username and password:
            uri = f"mongodb://{username}:{password}@{host}:{port}/{database}"
        else:
            uri = f"mongodb://{host}:{port}/{database}"
        
        print(f"🔗 Conectando a: {uri}")
        
        # Leer contenido del archivo
        content = await file.read()
        print(f"📄 Archivo leído: {len(content)} bytes")
        
        # Determinar formato del archivo
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nombre de archivo no proporcionado"
            )
        
        file_extension = file.filename.split('.')[-1].lower()
        print(f"📋 Extensión de archivo: {file_extension}")
        
        if file_extension == 'json':
            # Importar JSON
            try:
                data = json.loads(content.decode('utf-8'))
                print(f"✅ JSON parseado correctamente")
            except json.JSONDecodeError as e:
                print(f"❌ Error parseando JSON: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Archivo JSON inválido"
                )
            
            # Conectar a MongoDB
            try:
                client = AsyncIOMotorClient(uri)
                db = client[database]
                
                # Verificar conexión
                await client.admin.command('ping')
                print(f"✅ Conexión a MongoDB establecida")
            except Exception as e:
                print(f"❌ Error conectando a MongoDB: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error conectando a la base de datos: {str(e)}"
                )
            
            imported_count = 0
            collections_processed = 0
            
            try:
                # Determinar estructura del archivo
                if isinstance(data, dict):
                    # Verificar si es formato de backup completo
                    if "metadata" in data and "data" in data:
                        print("📊 Formato de backup completo detectado")
                        collections_data = data["data"]
                    else:
                        print("📊 Formato directo detectado")
                        collections_data = data
                    
                    # Procesar cada colección
                    for collection_name, documents in collections_data.items():
                        if not isinstance(documents, list):
                            print(f"⚠️  Saltando {collection_name}: no es una lista")
                            continue
                        
                        # Mostrar estadísticas antes de la importación
                        collection = db[collection_name]
                        existing_count = await collection.count_documents({})
                        
                        print(f"📥 Procesando colección: {collection_name}")
                        print(f"   📊 Documentos existentes: {existing_count}")
                        print(f"   📥 Documentos a importar: {len(documents)}")
                        print(f"   🎯 Modo: {mode.upper()}")
                        
                        # Obtener colección
                        collection = db[collection_name]
                        
                        if documents:
                            if mode == "replace":
                                # Modo REPLACE: eliminar todo y reemplazar
                                print(f"   🔄 Modo REPLACE: eliminando datos existentes...")
                                result = await collection.delete_many({})
                                if result.deleted_count > 0:
                                    print(f"   🗑️  Eliminados {result.deleted_count} documentos existentes")
                                
                                # Validar y procesar ObjectIds antes de insertar
                                processed_documents = []
                                for doc in documents:
                                    processed_doc = process_document_for_import(doc)
                                    if processed_doc:
                                        processed_documents.append(processed_doc)
                                
                                if processed_documents:
                                    await collection.insert_many(processed_documents)
                                    imported_count += len(processed_documents)
                                    print(f"   ✅ Reemplazados {len(processed_documents)} documentos")
                                    
                                    # Verificar integridad después de la importación
                                    await verify_import_integrity(db, collection_name, len(processed_documents))
                                else:
                                    print(f"   ⚠️  No se procesaron documentos válidos")
                                
                            elif mode == "upsert":
                                # Modo UPSERT: actualizar si existe, insertar si no
                                print(f"   🔄 Modo UPSERT: actualizando/insertando...")
                                upserted_count = 0
                                for doc in documents:
                                    processed_doc = process_document_for_import(doc)
                                    if not processed_doc:
                                        print(f"   ⚠️  Saltando documento inválido")
                                        continue
                                    
                                    if '_id' in processed_doc:
                                        # Usar _id como criterio de búsqueda
                                        result = await collection.replace_one(
                                            {"_id": processed_doc['_id']}, 
                                            processed_doc, 
                                            upsert=True
                                        )
                                        if result.upserted_id:
                                            print(f"   ➕ Insertado documento con _id: {processed_doc['_id']}")
                                        else:
                                            print(f"   🔄 Actualizado documento con _id: {processed_doc['_id']}")
                                    else:
                                        # Sin _id, insertar directamente
                                        await collection.insert_one(processed_doc)
                                        print(f"   ➕ Insertado documento sin _id")
                                    upserted_count += 1
                                
                                imported_count += upserted_count
                                print(f"   ✅ Procesados {upserted_count} documentos (upsert)")
                                
                                # Verificar integridad después de la importación
                                await verify_import_integrity(db, collection_name, upserted_count)
                                
                            else:
                                # Modo INSERT: insertar solo documentos nuevos (evitar duplicados)
                                print(f"   ➕ Modo INSERT: insertando solo documentos nuevos...")
                                try:
                                    # Validar y procesar ObjectIds antes de insertar
                                    processed_documents = []
                                    skipped_count = 0
                                    
                                    for doc in documents:
                                        processed_doc = process_document_for_import(doc)
                                        if not processed_doc:
                                            continue
                                        
                                        # Verificar si el documento ya existe
                                        exists_query = {}
                                        if '_id' in processed_doc:
                                            exists_query['_id'] = processed_doc['_id']
                                        else:
                                            # Sin _id, usar otros campos únicos según la colección
                                            exists_query = await get_unique_query_for_collection(collection_name, processed_doc)
                                        
                                        if exists_query:
                                            existing_doc = await collection.find_one(exists_query)
                                            if existing_doc:
                                                print(f"   ⚠️  Documento ya existe, saltando: {existing_doc.get('_id', 'sin _id')}")
                                                skipped_count += 1
                                                continue
                                        
                                        processed_documents.append(processed_doc)
                                    
                                    if processed_documents:
                                        await collection.insert_many(processed_documents)
                                        imported_count += len(processed_documents)
                                        print(f"   ✅ Insertados {len(processed_documents)} documentos nuevos")
                                        print(f"   ⏭️  Saltados {skipped_count} documentos existentes")
                                        
                                        # Verificar integridad después de la importación
                                        await verify_import_integrity(db, collection_name, len(processed_documents))
                                    else:
                                        print(f"   ⚠️  No se insertaron documentos nuevos")
                                        print(f"   ⏭️  Todos los {len(documents)} documentos ya existían")
                                except Exception as e:
                                    print(f"   ❌ Error en modo INSERT: {e}")
                                    # Intentar insertar uno por uno para manejar errores individuales
                                    manual_count = 0
                                    for doc in documents:
                                        try:
                                            processed_doc = process_document_for_import(doc)
                                            if processed_doc:
                                                # Verificar duplicados antes de insertar
                                                existing = await collection.find_one({"_id": processed_doc.get('_id', "invalid")})
                                                if not existing:
                                                    await collection.insert_one(processed_doc)
                                                    manual_count += 1
                                        except Exception:
                                            # Ignorar errores individuales
                                            pass
                                    
                                    if manual_count > 0:
                                        imported_count += manual_count
                                        print(f"   ✅ Insertados manualmente {manual_count} documentos")
                        else:
                            print(f"   ⚠️  Colección vacía, saltando...")
                        
                        collections_processed += 1
                    
                    print(f"🎉 Importación completada: {imported_count} documentos en {collections_processed} colecciones")
                    
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Formato de archivo no soportado. Debe ser un objeto JSON"
                    )
                
            except Exception as e:
                print(f"❌ Error durante la importación: {e}")
                import traceback
                print(f"📋 Traceback completo: {traceback.format_exc()}")
                
                # Determinar el tipo de error para dar un mensaje más específico
                error_msg = str(e)
                if "duplicate key" in error_msg.lower():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Error de duplicados: algunos documentos ya existen. Use modo 'replace' o 'upsert'."
                    )
                elif "connection" in error_msg.lower():
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Error de conexión a la base de datos. Verifique la configuración."
                    )
                elif "authentication" in error_msg.lower():
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Error de autenticación. Verifique las credenciales de la base de datos."
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Error durante la importación: {error_msg}"
                    )
            finally:
                client.close()
                print(f"🔌 Conexión a MongoDB cerrada")
            
            # Log de auditoría
            try:
                await log_audit(
                    user=current_user,
                    action=AuditAction.IMPORT,
                    module=AuditModule.ACCOUNTS,
                    description=f"Base de datos importada: {file.filename}",
                    resource_id=None,
                    resource_type="database",
                    new_values={
                        "filename": file.filename,
                        "mode": mode,
                        "imported_documents": imported_count,
                        "collections_processed": collections_processed
                    },
                    ip_address="127.0.0.1",
                    user_agent="Database Import"
                )
                print(f"📝 Log de auditoría registrado")
            except Exception as e:
                print(f"⚠️  Error registrando auditoría: {e}")
            
            return {
                "success": True,
                "message": f"Importación exitosa: {imported_count} documentos importados",
                "imported": imported_count,
                "collections_processed": collections_processed
            }
            
        elif file_extension == 'csv':
            # Para CSV, necesitaríamos más información sobre la colección destino
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Importación CSV requiere especificar la colección destino"
            )
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de archivo no soportado. Use JSON o CSV"
            )
        
    except HTTPException:
        # Re-lanzar HTTPExceptions sin modificar
        raise
    except Exception as e:
        print(f"❌ Error inesperado en importación: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.post("/backup")
async def create_backup(
    request: Request,
    host: str = "localhost",
    port: int = 27017,
    database: str = "sistema_contable_ec",
    username: Optional[str] = None,
    password: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Crear backup completo de la base de datos"""
    try:
        # Construir URI de conexión
        if username and password:
            uri = f"mongodb://{username}:{password}@{host}:{port}/{database}"
        else:
            uri = f"mongodb://{host}:{port}/{database}"
        
        # Verificar conexión
        client = AsyncIOMotorClient(uri)
        await client.admin.command('ping')
        db = client[database]
        
        # Obtener todas las colecciones
        collections = await db.list_collection_names()
        
        # Crear backup completo
        backup_data = {
            "metadata": {
                "database": database,
                "host": host,
                "port": port,
                "backup_date": datetime.now().isoformat(),
                "created_by": str(current_user.id),
                "collections": collections
            },
            "data": {}
        }
        
        for collection_name in collections:
            collection = db[collection_name]
            documents = await collection.find({}).to_list(None)
            backup_data["data"][collection_name] = documents
        
        client.close()
        
        # Crear archivo de backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_content = json.dumps(backup_data, indent=2, default=str)
        
        # Crear respuesta de streaming
        def generate():
            yield backup_content.encode('utf-8')
        
        return StreamingResponse(
            generate(),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=backup_completo_sistema_contable_{timestamp}.json"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear backup: {str(e)}"
        )

@router.get("/collections")
async def get_collections_info(
    host: str = "localhost",
    port: int = 27017,
    database: str = "sistema_contable_ec",
    username: Optional[str] = None,
    password: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Obtener información detallada de las colecciones"""
    try:
        # Construir URI de conexión
        if username and password:
            uri = f"mongodb://{username}:{password}@{host}:{port}/{database}"
        else:
            uri = f"mongodb://{host}:{port}/{database}"
        
        # Conectar a MongoDB
        client = AsyncIOMotorClient(uri)
        db = client[database]
        
        # Obtener información de colecciones
        collections = await db.list_collection_names()
        collection_info = []
        
        for collection_name in collections:
            collection = db[collection_name]
            count = await collection.count_documents({})
            
            # Obtener tamaño aproximado
            stats = await db.command("collStats", collection_name)
            size_bytes = stats.get("size", 0)
            
            collection_info.append({
                "name": collection_name,
                "count": count,
                "size_bytes": size_bytes,
                "size_mb": round(size_bytes / (1024 * 1024), 2)
            })
        
        client.close()
        
        return {
            "success": True,
            "collections": collection_info,
            "total_collections": len(collections),
            "total_documents": sum(c["count"] for c in collection_info),
            "total_size_mb": sum(c["size_mb"] for c in collection_info)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener información de colecciones: {str(e)}"
        )
