# Documentación Técnica - Sistema Contable Ecuador

## Arquitectura del Sistema

### Stack Tecnológico

**Backend:**
- **FastAPI** 0.104.1 - Framework web moderno y rápido
- **MongoDB** 5.0+ - Base de datos NoSQL
- **Beanie** 1.23.6 - ODM para MongoDB
- **Motor** 3.3.2 - Driver asíncrono para MongoDB
- **Pydantic** 2.5.0 - Validación de datos
- **JWT** - Autenticación con tokens
- **Bcrypt** - Hashing de contraseñas

**Frontend:**
- **Vue 3** 3.3.8 - Framework JavaScript reactivo
- **Vite** 5.0.0 - Build tool y dev server
- **Pinia** 2.1.7 - State management
- **Vue Router** 4.2.5 - Routing
- **Bootstrap** 5.3.2 - Framework CSS
- **FontAwesome** 6.5.1 - Iconos
- **Chart.js** 4.4.0 - Gráficos
- **Axios** 1.6.2 - Cliente HTTP

### Arquitectura de Microservicios

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (Vue 3)       │◄──►│   (FastAPI)     │◄──►│   (MongoDB)     │
│   Port: 5173    │    │   Port: 8000    │    │   Port: 27017   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Estructura de Base de Datos

### Colecciones MongoDB

#### 1. Users (Usuarios)
```javascript
{
  _id: ObjectId,
  username: String (unique),
  email: String (unique),
  password_hash: String,
  first_name: String,
  last_name: String,
  role: Enum['admin', 'contador', 'auditor', 'interno'],
  status: Enum['active', 'inactive', 'suspended'],
  permissions: Array[String],
  companies: Array[ObjectId],
  last_login: Date,
  created_at: Date,
  updated_at: Date,
  created_by: ObjectId,
  audit_log: Array[AuditEntry]
}
```

#### 2. Companies (Empresas)
```javascript
{
  _id: ObjectId,
  name: String,
  ruc: String (unique),
  legal_name: String,
  address: String,
  phone: String,
  email: String,
  status: Enum['active', 'inactive', 'suspended'],
  fiscal_year_start: Number (1-12),
  currency: String (default: 'USD'),
  created_at: Date,
  updated_at: Date,
  created_by: ObjectId
}
```

#### 3. Accounts (Cuentas Contables)
```javascript
{
  _id: ObjectId,
  code: String,
  name: String,
  description: String,
  account_type: Enum['activo', 'pasivo', 'patrimonio', 'ingresos', 'gastos', 'costos'],
  nature: Enum['deudora', 'acreedora'],
  parent_code: String,
  level: Number,
  company_id: ObjectId,
  is_active: Boolean,
  is_editable: Boolean,
  created_at: Date,
  updated_at: Date,
  created_by: ObjectId
}
```

#### 4. Journal Entries (Asientos Contables)
```javascript
{
  _id: ObjectId,
  entry_number: String (unique),
  date: Date,
  description: String,
  entry_type: Enum['manual', 'automatic', 'adjustment', 'closing'],
  status: Enum['draft', 'posted', 'reversed'],
  lines: Array[JournalLine],
  total_debit: Number,
  total_credit: Number,
  company_id: ObjectId,
  created_by: ObjectId,
  approved_by: ObjectId,
  approved_at: Date,
  created_at: Date,
  updated_at: Date
}
```

#### 5. Audit Logs (Logs de Auditoría)
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  username: String,
  action: Enum['create', 'read', 'update', 'delete', 'login', 'logout', 'approve', 'reject', 'export', 'import'],
  module: Enum['auth', 'users', 'companies', 'accounts', 'journal', 'reports', 'sri', 'assets', 'payables', 'receivables'],
  resource_id: ObjectId,
  resource_type: String,
  description: String,
  ip_address: String,
  user_agent: String,
  company_id: ObjectId,
  old_values: Object,
  new_values: Object,
  timestamp: Date
}
```

## API Endpoints

### Autenticación
- `POST /api/auth/login` - Iniciar sesión
- `POST /api/auth/logout` - Cerrar sesión
- `POST /api/auth/refresh` - Renovar token
- `GET /api/auth/me` - Información del usuario actual
- `POST /api/auth/register` - Registrar usuario (solo admin)

### Usuarios
- `GET /api/users` - Listar usuarios
- `GET /api/users/{id}` - Obtener usuario
- `POST /api/users` - Crear usuario
- `PUT /api/users/{id}` - Actualizar usuario
- `DELETE /api/users/{id}` - Eliminar usuario
- `POST /api/users/{id}/reset-password` - Restablecer contraseña

### Empresas
- `GET /api/companies` - Listar empresas
- `GET /api/companies/{id}` - Obtener empresa
- `POST /api/companies` - Crear empresa
- `PUT /api/companies/{id}` - Actualizar empresa
- `DELETE /api/companies/{id}` - Eliminar empresa

### Cuentas Contables
- `GET /api/accounts` - Listar cuentas
- `GET /api/accounts/{id}` - Obtener cuenta
- `POST /api/accounts` - Crear cuenta
- `PUT /api/accounts/{id}` - Actualizar cuenta
- `DELETE /api/accounts/{id}` - Eliminar cuenta
- `GET /api/accounts/{company_id}/balance` - Balance de cuentas

### Diario Contable
- `GET /api/journal` - Listar asientos
- `GET /api/journal/{id}` - Obtener asiento
- `POST /api/journal` - Crear asiento
- `PUT /api/journal/{id}` - Actualizar asiento
- `DELETE /api/journal/{id}` - Eliminar asiento
- `POST /api/journal/{id}/approve` - Aprobar asiento

### Reportes
- `GET /api/reports/balance-general` - Balance General
- `GET /api/reports/estado-resultados` - Estado de Resultados
- `GET /api/reports/libro-mayor` - Libro Mayor
- `GET /api/reports/auditoria` - Logs de Auditoría
- `POST /api/reports/export/{type}` - Exportar reporte

### SRI
- `GET /api/sri/formulario-103` - Formulario 103
- `GET /api/sri/formulario-104` - Formulario 104
- `GET /api/sri/rdep` - RDEP
- `POST /api/sri/enviar-sri/{formulario}` - Enviar al SRI
- `GET /api/sri/estado-envios` - Estado de envíos
- `GET /api/sri/configuracion` - Configuración SRI

## Sistema de Permisos

### Roles y Permisos

#### Admin
- Acceso completo al sistema
- Gestión de usuarios y empresas
- Configuración del sistema
- Acceso a auditoría

#### Contador
- Gestión contable completa
- Creación y aprobación de asientos
- Generación de reportes
- Declaraciones SRI

#### Auditor
- Solo lectura
- Acceso a reportes
- Logs de auditoría

#### Interno
- Acceso limitado
- Solo lectura según permisos

### Matriz de Permisos

| Módulo | Admin | Contador | Auditor | Interno |
|--------|-------|----------|---------|---------|
| Usuarios | CRUD | - | R | - |
| Empresas | CRUD | R | R | R |
| Cuentas | CRUD | CRU | R | R |
| Diario | CRUD | CRUD | R | R |
| Reportes | R | R | R | R |
| SRI | R | R | - | - |
| Auditoría | R | - | R | - |

## Seguridad

### Autenticación
- JWT con refresh tokens
- Tokens de acceso expiran en 30 minutos
- Tokens de refresh expiran en 7 días
- Hashing de contraseñas con bcrypt

### Autorización
- Middleware de permisos por endpoint
- Validación de roles en frontend
- Separación de datos por empresa

### Auditoría
- Log de todas las acciones
- Trazabilidad completa
- IP y user agent registrados
- Valores antiguos y nuevos

## Despliegue

### Desarrollo Local
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
python scripts/init_db.py
python scripts/run_server.py

# Frontend
cd frontend
npm install
npm run dev
```

### Docker
```bash
# Iniciar todos los servicios
docker-compose up -d

# Solo base de datos
docker-compose up -d mongodb

# Rebuild y restart
docker-compose up --build -d
```

### Producción
1. Configurar variables de entorno
2. Usar base de datos MongoDB en la nube
3. Configurar proxy reverso (Nginx)
4. Implementar HTTPS
5. Configurar backup automático

## Monitoreo y Logs

### Logs de Aplicación
- Logs de FastAPI con uvicorn
- Logs de MongoDB
- Logs de Nginx (en producción)

### Métricas
- Tiempo de respuesta de API
- Uso de memoria y CPU
- Conexiones a base de datos
- Errores y excepciones

### Alertas
- Servicios caídos
- Errores críticos
- Uso excesivo de recursos
- Intentos de acceso no autorizados

## Mantenimiento

### Backup
- Backup diario de MongoDB
- Backup de archivos de configuración
- Backup de logs de auditoría

### Actualizaciones
- Actualizaciones de seguridad
- Nuevas funcionalidades
- Mejoras de rendimiento
- Corrección de bugs

### Escalabilidad
- Horizontal: Múltiples instancias de backend
- Vertical: Más recursos por instancia
- Base de datos: Replicación y sharding
- Cache: Redis para sesiones y datos frecuentes

## Troubleshooting

### Problemas Comunes

#### Error de conexión a MongoDB
```bash
# Verificar que MongoDB esté ejecutándose
sudo systemctl status mongod

# Verificar logs
sudo journalctl -u mongod

# Verificar configuración
cat /etc/mongod.conf
```

#### Error de permisos en frontend
```bash
# Limpiar cache de npm
npm cache clean --force

# Reinstalar dependencias
rm -rf node_modules package-lock.json
npm install
```

#### Error de JWT
- Verificar SECRET_KEY en .env
- Verificar expiración de tokens
- Verificar formato de token en headers

### Logs de Debug
```bash
# Backend con debug
DEBUG=true uvicorn app.main:app --reload

# Frontend con debug
VITE_DEBUG=true npm run dev
```

## Contribución

### Estándares de Código
- Python: PEP 8, Black formatter
- JavaScript: ESLint, Prettier
- Commits: Conventional Commits
- Documentación: Markdown

### Proceso de Desarrollo
1. Fork del repositorio
2. Crear rama feature
3. Implementar cambios
4. Tests unitarios
5. Pull request
6. Code review
7. Merge a main

### Testing
```bash
# Backend tests
pytest tests/

# Frontend tests
npm run test

# E2E tests
npm run test:e2e
```

## Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo LICENSE para más detalles.

## Contacto

- **Desarrollador**: Bryam
- **Email**: bryam@ejemplo.com
- **GitHub**: @bryam
- **Documentación**: Ver README.md










