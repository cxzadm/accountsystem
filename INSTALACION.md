# Guía de Instalación - Sistema Contable  Accescont Ecuador

## Requisitos Previos

### Backend
- Python 3.8 o superior
- MongoDB 4.4 o superior
- pip (gestor de paquetes de Python)

### Frontend
- Node.js 16 o superior
- npm o yarn

## Instalación del Backend

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd sistema-account
```

### 2. Crear entorno virtual
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
# Copiar archivo de ejemplo
copy env.example .env

# Editar .env con tus configuraciones
# MONGODB_URL=mongodb://localhost:27017
# SECRET_KEY=tu-clave-secreta-super-segura
```

### 5. Inicializar base de datos
```bash
python scripts/init_db.py
```

### 6. Ejecutar servidor
```bash
python scripts/run_server.py
```

El backend estará disponible en: http://localhost:8000
Documentación API: http://localhost:8000/docs

## Instalación del Frontend

### 1. Navegar al directorio frontend
```bash
cd frontend
```

### 2. Instalar dependencias
```bash
npm install
```

### 3. Ejecutar servidor de desarrollo
```bash
npm run dev
```

El frontend estará disponible en: http://localhost:5173

## Acceso al Sistema

### Credenciales por defecto:
- **Administrador**: admin / admin123
- **Contador**: contador / contador123

### Funcionalidades disponibles:
- ✅ Gestión de usuarios y empresas
- ✅ Plan de cuentas contables
- ✅ Diario contable con doble partida
- ✅ Reportes contables básicos
- ✅ Sistema de auditoría
- ✅ Declaraciones SRI (simuladas)

## Estructura del Proyecto

```
sistema-account/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── models/         # Modelos de datos
│   │   ├── routes/         # Endpoints de la API
│   │   ├── auth/           # Autenticación
│   │   └── main.py         # Aplicación principal
│   ├── scripts/            # Scripts de utilidad
│   └── requirements.txt    # Dependencias Python
├── frontend/               # Aplicación Vue.js
│   ├── src/
│   │   ├── components/     # Componentes Vue
│   │   ├── views/          # Vistas/páginas
│   │   ├── stores/         # Stores Pinia
│   │   └── router/         # Configuración de rutas
│   └── package.json        # Dependencias Node.js
└── README.md              # Documentación principal
```

## Solución de Problemas

### Error de conexión a MongoDB
- Verificar que MongoDB esté ejecutándose
- Comprobar la URL de conexión en .env
- Verificar que el puerto 27017 esté disponible

### Error de dependencias Python
- Verificar que Python 3.8+ esté instalado
- Recrear el entorno virtual
- Actualizar pip: `pip install --upgrade pip`

### Error de dependencias Node.js
- Verificar que Node.js 16+ esté instalado
- Limpiar caché: `npm cache clean --force`
- Eliminar node_modules y reinstalar

### Puerto ya en uso
- Cambiar puerto en vite.config.js (frontend)
- Cambiar puerto en scripts/run_server.py (backend)

## Desarrollo

### Backend
```bash
# Ejecutar con recarga automática
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Ejecutar tests
pytest

# Formatear código
black .
```

### Frontend
```bash
# Ejecutar en modo desarrollo
npm run dev

# Construir para producción
npm run build

# Linter
npm run lint
```

## Producción

### Backend
1. Configurar variables de entorno de producción
2. Usar un servidor WSGI como Gunicorn
3. Configurar proxy reverso (Nginx)
4. Usar base de datos MongoDB en la nube

### Frontend
1. Ejecutar `npm run build`
2. Servir archivos estáticos con Nginx
3. Configurar HTTPS
4. Configurar variables de entorno

## Soporte

Para reportar problemas o solicitar funcionalidades:
1. Crear un issue en el repositorio
2. Describir el problema detalladamente
3. Incluir logs de error si es necesario
4. Especificar versión del sistema operativo y navegador











