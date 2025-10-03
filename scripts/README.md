# Scripts de Configuración Inicial - Sistema Contable Ecuador

Esta carpeta contiene scripts para configurar datos iniciales en el sistema contable, especialmente útil para la primera configuración o migración de datos.

## 📋 Scripts Disponibles

### 1. `setup_initial_data.py` - Configuración Inicial Completa
**Propósito**: Configuración completa del sistema desde cero

**Características**:
- ✅ Crear usuario administrador
- ✅ Crear empresa de ejemplo
- ✅ Crear plan de cuentas básico
- ✅ Crear tipos de documentos
- ✅ Importar archivos de backup
- ✅ Verificar estado del sistema

**Uso**:
```bash
python scripts/setup_initial_data.py
```

### 2. `import_initial_data.py` - Importador Avanzado
**Propósito**: Importación completa con interfaz interactiva

**Características**:
- ✅ Selección interactiva de archivos
- ✅ Validación de estructura de backup
- ✅ Múltiples modos de importación (insert, upsert, replace)
- ✅ Verificación de datos existentes
- ✅ Soporte para diferentes formatos

**Uso**:
```bash
# Interfaz interactiva
python scripts/import_initial_data.py

# Con parámetros específicos
python scripts/import_initial_data.py --file backup.json --mode replace

# Buscar en directorio específico
python scripts/import_initial_data.py --dir /path/to/backups
```

**Parámetros**:
- `--file, -f`: Ruta específica al archivo de backup
- `--dir, -d`: Directorio donde buscar archivos
- `--mode, -m`: Modo de importación (insert/upsert/replace)
- `--force`: Forzar importación aunque existan datos
- `--mongodb-url`: URL personalizada de MongoDB
- `--database`: Nombre personalizado de la base de datos

### 3. `quick_import.py` - Importación Rápida
**Propósito**: Importación simple y rápida

**Características**:
- ✅ Importación directa sin interfaz
- ✅ Ideal para automatización
- ✅ Soporte para archivos JSON
- ✅ Limpieza automática de datos existentes

**Uso**:
```bash
python scripts/quick_import.py backup_sistema_contable_2025-09-30.json
```

## 🚀 Guía de Uso

### Primera Configuración del Sistema

1. **Configuración completa (recomendado)**:
   ```bash
   python scripts/setup_initial_data.py
   ```
   - Crea usuario administrador
   - Crea empresa de ejemplo
   - Configura plan de cuentas básico
   - Listo para usar

2. **Solo importar datos existentes**:
   ```bash
   python scripts/import_initial_data.py
   ```
   - Selecciona archivo de backup
   - Importa todos los datos
   - Mantiene estructura completa

### Migración de Datos

1. **Importación rápida**:
   ```bash
   python scripts/quick_import.py mi_backup.json
   ```

2. **Importación con opciones**:
   ```bash
   python scripts/import_initial_data.py --file backup.json --mode upsert
   ```

### Verificación del Sistema

```bash
python scripts/setup_initial_data.py
# Seleccionar opción 5: "Ver estado del sistema"
```

## 📁 Formatos de Archivo Soportados

### Backup Completo (Recomendado)
```json
{
  "metadata": {
    "database": "sistema_contable_ec",
    "backup_date": "2025-09-30T10:30:00",
    "created_by": "admin",
    "collections": ["accounts", "companies", "users"]
  },
  "data": {
    "accounts": [...],
    "companies": [...],
    "users": [...]
  }
}
```

### Datos Directos
```json
{
  "accounts": [...],
  "companies": [...],
  "users": [...],
  "journal_entries": [...]
}
```

## 🔧 Configuración

### Variables de Entorno
Los scripts usan automáticamente la configuración del proyecto:
- `MONGODB_URL`: URL de conexión a MongoDB
- `DATABASE_NAME`: Nombre de la base de datos

### Personalización
```bash
# Usar configuración personalizada
python scripts/import_initial_data.py \
  --mongodb-url "mongodb://localhost:27017" \
  --database "mi_base_datos"
```

## 📊 Colecciones Soportadas

Los scripts pueden importar las siguientes colecciones:

- ✅ `accounts` - Cuentas contables
- ✅ `companies` - Empresas
- ✅ `users` - Usuarios
- ✅ `journal_entries` - Asientos contables
- ✅ `ledger_entries` - Mayor general
- ✅ `audit_logs` - Logs de auditoría
- ✅ `document_types` - Tipos de documento
- ✅ `document_reservations` - Reservas de documentos

## ⚠️ Consideraciones Importantes

### Seguridad
- Los scripts requieren acceso completo a la base de datos
- Se recomienda hacer backup antes de importar
- Verificar permisos de usuario antes de ejecutar

### Modos de Importación
- **`insert`**: Solo inserta nuevos documentos
- **`upsert`**: Actualiza si existe, inserta si no
- **`replace`**: Elimina datos existentes y reemplaza

### Datos Existentes
- Los scripts verifican si ya existen datos
- Se puede forzar la importación con `--force`
- Se recomienda hacer backup antes de reemplazar

## 🆘 Solución de Problemas

### Error de Conexión
```
❌ Error conectando a MongoDB: [Errno 111] Connection refused
```
**Solución**: Verificar que MongoDB esté ejecutándose y la URL sea correcta

### Error de Permisos
```
❌ Error: No se pudo importar las dependencias del proyecto
```
**Solución**: Ejecutar desde el directorio raíz del proyecto

### Error de Archivo
```
❌ Archivo no encontrado: backup.json
```
**Solución**: Verificar la ruta del archivo y permisos de lectura

### Error de Formato
```
❌ Archivo JSON inválido
```
**Solución**: Verificar que el archivo sea un JSON válido con la estructura correcta

## 📞 Soporte

Para problemas o dudas:
1. Verificar logs de error
2. Comprobar configuración de MongoDB
3. Validar formato del archivo de backup
4. Revisar permisos de usuario

## 🔄 Actualizaciones

Los scripts se actualizan automáticamente con el proyecto. Para obtener la última versión:

```bash
git pull origin main
```

---

*Scripts desarrollados para el Sistema Contable Ecuador - Versión 1.0*


