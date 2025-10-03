# Base de Datos - Sistema Contable Ecuador

## Base de datos: `sistema_contable_ec` en MongoDB

Estás trabajando con una base de datos contable estructurada y funcional, con varias colecciones clave que apuntan a un sistema de contabilidad general automatizado, posiblemente multiempresa.

## 📂 Colecciones detectadas:

| Colección | Descripción rápida |
|-----------|-------------------|
| `accounts` | Catálogo de cuentas contables (activo, pasivo...). |
| `audit_logs` | Registro de auditoría (acciones del sistema/usuarios). |
| `companies` | Información de las empresas registradas en el sistema. |
| `document_reservations` | Probablemente reservaciones de consecutivos/documentos. |
| `document_types` | Tipos de documentos contables (CE, DI, etc.). |
| `journal_entries` | Asientos contables (comprobantes de diario). |
| `ledger_entries` | Movimientos individuales del libro mayor. |
| `users` | Usuarios registrados del sistema. |

---

## 📋 Descripción Detallada de Colecciones

### 1. **accounts** - Plan de Cuentas Contables

**Propósito**: Almacena el catálogo de cuentas contables con estructura jerárquica.

**Campos principales**:
- `code`: Código de la cuenta (ej: "1010101")
- `name`: Nombre de la cuenta
- `description`: Descripción opcional
- `account_type`: Tipo de cuenta (activo, pasivo, patrimonio, ingresos, gastos, costos)
- `nature`: Naturaleza (deudora, acreedora)
- `parent_code`: Código de la cuenta padre para jerarquía
- `level`: Nivel jerárquico (1-5)
- `company_id`: ID de la empresa propietaria
- `is_active`: Estado activo/inactivo
- `is_editable`: Si la cuenta puede ser editada
- `initial_debit_balance`: Saldo inicial débito
- `initial_credit_balance`: Saldo inicial crédito
- `current_debit_balance`: Saldo actual débito
- `current_credit_balance`: Saldo actual crédito
- `last_transaction_date`: Fecha del último movimiento
- `created_at`, `updated_at`: Timestamps
- `created_by`: Usuario que creó la cuenta

**Funcionalidades**:
- ✅ Gestión jerárquica de cuentas (padre-hijo)
- ✅ Cálculo automático de saldos padre
- ✅ Importación/exportación de plan de cuentas
- ✅ Saldos iniciales configurables
- ✅ Búsqueda inteligente
- ✅ Validación de códigos únicos por empresa

---

### 2. **audit_logs** - Registro de Auditoría

**Propósito**: Registra todas las acciones del sistema para auditoría y trazabilidad.

**Campos principales**:
- `user_id`: ID del usuario que realizó la acción
- `username`: Nombre de usuario
- `action`: Acción realizada (create, read, update, delete, login, logout, approve, reject, export, import)
- `module`: Módulo afectado (auth, users, companies, accounts, journal, reports, sri, assets, payables, receivables)
- `resource_id`: ID del recurso afectado
- `resource_type`: Tipo de recurso
- `description`: Descripción de la acción
- `ip_address`: Dirección IP del usuario
- `user_agent`: Navegador/dispositivo
- `company_id`: Empresa relacionada
- `old_values`: Valores anteriores (para updates)
- `new_values`: Valores nuevos (para creates/updates)
- `timestamp`: Fecha y hora de la acción

**Funcionalidades**:
- ✅ Registro automático de todas las operaciones
- ✅ Trazabilidad completa de cambios
- ✅ Información de contexto (IP, navegador)
- ✅ Valores antes y después para auditoría
- ✅ Filtrado por módulo y acción

---

### 3. **companies** - Empresas

**Propósito**: Información de las empresas registradas en el sistema.

**Campos principales**:
- `name`: Nombre comercial
- `ruc`: RUC de la empresa
- `legal_name`: Razón social
- `address`: Dirección
- `phone`: Teléfono
- `email`: Email de contacto
- `status`: Estado (active, inactive, suspended)
- `fiscal_year_start`: Mes de inicio del año fiscal (1-12)
- `currency`: Moneda (USD por defecto)
- `created_at`, `updated_at`: Timestamps
- `created_by`: Usuario que creó la empresa

**Funcionalidades**:
- ✅ Gestión multiempresa
- ✅ Configuración fiscal por empresa
- ✅ Estados de empresa
- ✅ Información de contacto

---

### 4. **document_reservations** - Reservas de Documentos

**Propósito**: Control de numeración consecutiva de documentos contables.

**Campos principales**:
- `company_id`: ID de la empresa
- `document_type_id`: ID del tipo de documento
- `document_code`: Código del documento (ej: "CE")
- `sequence`: Número secuencial
- `number`: Número completo (ej: "CE-00001")
- `status`: Estado (reserved, used, cancelled)
- `journal_entry_id`: ID del asiento que usa la reserva
- `reserved_by`: Usuario que reservó
- `reserved_at`: Fecha de reserva
- `used_at`: Fecha de uso

**Funcionalidades**:
- ✅ Control de numeración consecutiva
- ✅ Reserva de números de documentos
- ✅ Estados de reserva
- ✅ Vinculación con asientos contables

---

### 5. **document_types** - Tipos de Documentos

**Propósito**: Configuración de tipos de documentos contables según normativa SRI.

**Campos principales**:
- `code`: Código del documento (CE, CI, 01, 21, etc.)
- `name`: Nombre del documento
- `control_number`: Último número asignado
- `establishment_point`: Punto de emisión (001-001)
- `receipt_type`: Tipo de comprobante SRI
- `bank_movement`: Movimiento bancario (D/C)
- `customer_movement`: Movimiento cliente (D/C)
- `supplier_movement`: Movimiento proveedor (D/C)
- `product_movement`: Movimiento producto (I/E)
- `is_electronic`: Si es documento electrónico
- `responsible_code`: Código del responsable
- `responsible_name`: Nombre del responsable
- `next_sequence`: Próximo número secuencial
- `padding`: Longitud del número (ej: 5 para "00001")
- `company_id`: Empresa propietaria
- `is_active`: Estado activo/inactivo

**Funcionalidades**:
- ✅ Configuración según normativa SRI
- ✅ Control de numeración automática
- ✅ Documentos electrónicos
- ✅ Responsables por documento
- ✅ Movimientos contables automáticos

---

### 6. **journal_entries** - Asientos Contables

**Propósito**: Registro de asientos contables (comprobantes de diario).

**Campos principales**:
- `entry_number`: Número del asiento (ej: "AS-2024-000001")
- `date`: Fecha del asiento
- `description`: Descripción del asiento
- `entry_type`: Tipo (manual, automatic, adjustment, closing)
- `status`: Estado (draft, posted, reversed)
- `document_type_id`: ID del tipo de documento
- `document_type_code`: Código del tipo de documento
- `lines`: Array de líneas del asiento
  - `account_code`: Código de cuenta
  - `account_name`: Nombre de cuenta
  - `description`: Descripción de la línea
  - `debit`: Monto débito
  - `credit`: Monto crédito
  - `reference`: Referencia
- `total_debit`: Total débitos
- `total_credit`: Total créditos
- `company_id`: Empresa
- `created_by`: Usuario creador
- `responsable`: Responsable del asiento
- `approved_by`: Usuario que aprobó
- `approved_at`: Fecha de aprobación
- `created_at`, `updated_at`: Timestamps

**Funcionalidades**:
- ✅ Validación de doble partida
- ✅ Estados de asiento (borrador, aprobado, revertido)
- ✅ Mayorización automática
- ✅ Copia y reversión de asientos
- ✅ Aprobación de asientos
- ✅ Vinculación con tipos de documento

---

### 7. **ledger_entries** - Mayor General

**Propósito**: Movimientos individuales del libro mayor (resultado de mayorizar asientos).

**Campos principales**:
- `account_id`: ID de la cuenta
- `account_code`: Código de la cuenta
- `account_name`: Nombre de la cuenta
- `company_id`: Empresa
- `entry_type`: Tipo de entrada (initial, journal, adjustment, closing)
- `journal_entry_id`: ID del asiento origen
- `date`: Fecha del movimiento
- `description`: Descripción del movimiento
- `reference`: Referencia
- `debit_amount`: Monto débito
- `credit_amount`: Monto crédito
- `running_debit_balance`: Saldo acumulado débito
- `running_credit_balance`: Saldo acumulado crédito
- `created_at`: Timestamp
- `created_by`: Usuario creador

**Funcionalidades**:
- ✅ Generación automática al mayorizar asientos
- ✅ Saldos acumulados por cuenta
- ✅ Trazabilidad con asientos origen
- ✅ Diferentes tipos de entrada
- ✅ Consulta de mayor por cuenta
- ✅ Mayor general consolidado

---

### 8. **users** - Usuarios del Sistema

**Propósito**: Gestión de usuarios y autenticación.

**Campos principales**:
- `username`: Nombre de usuario
- `email`: Email del usuario
- `password_hash`: Hash de la contraseña
- `first_name`: Nombre
- `last_name`: Apellido
- `role`: Rol (admin, contador, auditor, interno)
- `status`: Estado (active, inactive, suspended)
- `permissions`: Array de permisos específicos
- `companies`: Array de IDs de empresas asignadas
- `last_login`: Último acceso
- `created_at`, `updated_at`: Timestamps
- `created_by`: Usuario que creó el registro
- `audit_log`: Array de entradas de auditoría

**Funcionalidades**:
- ✅ Autenticación JWT
- ✅ Roles y permisos granulares
- ✅ Asignación multiempresa
- ✅ Estados de usuario
- ✅ Auditoría de accesos
- ✅ Gestión de sesiones

---

## 🔗 Relaciones entre Colecciones

### Relaciones Principales:
1. **companies** ↔ **accounts**: Una empresa tiene múltiples cuentas
2. **companies** ↔ **journal_entries**: Una empresa tiene múltiples asientos
3. **companies** ↔ **ledger_entries**: Una empresa tiene múltiples movimientos
4. **journal_entries** ↔ **ledger_entries**: Un asiento genera múltiples movimientos
5. **accounts** ↔ **ledger_entries**: Una cuenta tiene múltiples movimientos
6. **users** ↔ **companies**: Un usuario puede acceder a múltiples empresas
7. **document_types** ↔ **journal_entries**: Un tipo de documento se usa en múltiples asientos
8. **document_reservations** ↔ **journal_entries**: Una reserva se usa en un asiento

### Flujo de Datos:
```
1. Usuario crea/importa cuentas → accounts
2. Usuario crea asiento → journal_entries
3. Asiento se mayoriza → ledger_entries (automático)
4. Saldos se actualizan → accounts (automático)
5. Todo se registra → audit_logs (automático)
```

---

## 🚀 Funcionalidades del Sistema

### Gestión Contable:
- ✅ **Plan de Cuentas**: Estructura jerárquica, importación/exportación
- ✅ **Asientos Contables**: Creación, edición, aprobación, mayorización
- ✅ **Mayor General**: Consulta por cuenta, consolidado, filtros avanzados
- ✅ **Saldos Iniciales**: Configuración y actualización masiva
- ✅ **Numeración**: Control consecutivo de documentos

### Características Técnicas:
- ✅ **Multiempresa**: Aislamiento de datos por empresa
- ✅ **Auditoría**: Registro completo de todas las operaciones
- ✅ **Seguridad**: Autenticación JWT, roles y permisos
- ✅ **Escalabilidad**: MongoDB con índices optimizados
- ✅ **Integridad**: Validaciones de doble partida y consistencia

### Reportes y Consultas:
- ✅ **Mayor General**: Por cuenta, por período, con filtros
- ✅ **Balance de Cuentas**: Saldos iniciales + movimientos
- ✅ **Asientos**: Listado con filtros por fecha, estado, tipo
- ✅ **Auditoría**: Trazabilidad completa de cambios

---

## 📊 Índices Recomendados

Para optimizar el rendimiento, se recomiendan los siguientes índices:

```javascript
// accounts
db.accounts.createIndex({ "company_id": 1, "code": 1 })
db.accounts.createIndex({ "company_id": 1, "is_active": 1 })
db.accounts.createIndex({ "company_id": 1, "parent_code": 1 })

// journal_entries
db.journal_entries.createIndex({ "company_id": 1, "date": -1 })
db.journal_entries.createIndex({ "company_id": 1, "status": 1 })
db.journal_entries.createIndex({ "company_id": 1, "entry_number": 1 })

// ledger_entries
db.ledger_entries.createIndex({ "company_id": 1, "account_id": 1, "date": 1 })
db.ledger_entries.createIndex({ "company_id": 1, "date": 1 })
db.ledger_entries.createIndex({ "journal_entry_id": 1 })

// audit_logs
db.audit_logs.createIndex({ "company_id": 1, "timestamp": -1 })
db.audit_logs.createIndex({ "user_id": 1, "timestamp": -1 })
db.audit_logs.createIndex({ "module": 1, "action": 1 })

// users
db.users.createIndex({ "email": 1 })
db.users.createIndex({ "username": 1 })
db.users.createIndex({ "companies": 1 })

// document_reservations
db.document_reservations.createIndex({ "company_id": 1, "document_type_id": 1 })
db.document_reservations.createIndex({ "company_id": 1, "status": 1 })

// document_types
db.document_types.createIndex({ "company_id": 1, "code": 1 })
db.document_types.createIndex({ "company_id": 1, "is_active": 1 })
```

---

## 🔧 Mantenimiento y Optimización

### Tareas de Mantenimiento:
1. **Limpieza de auditoría**: Archivar logs antiguos
2. **Optimización de índices**: Monitorear rendimiento
3. **Backup regular**: Respaldo de datos críticos
4. **Validación de integridad**: Verificar consistencia de saldos

### Monitoreo Recomendado:
- Rendimiento de consultas al mayor general
- Tiempo de respuesta en mayorización de asientos
- Uso de espacio en colecciones de auditoría
- Crecimiento de datos por empresa

---

*Documentación generada automáticamente basada en el análisis del código fuente del sistema contable.*


