# Sistema Contable  Accescont Ecuador

Sistema contable multiempresa con cumplimiento fiscal ecuatoriano (SRI, NIIF) desarrollado con Vue 3, FastAPI y MongoDB.

## 🏗️ Arquitectura

- **Frontend**: Vue 3 + Vite + Pinia + Bootstrap + FontAwesome
- **Backend**: FastAPI + MongoDB + Beanie ODM
- **Autenticación**: JWT con refresh tokens
- **Base de datos**: MongoDB con separación por empresa

## 🚀 Instalación

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📋 Módulos

- ✅ Autenticación y gestión de usuarios
- ✅ Catálogo de cuentas contables
- ✅ Diario contable con doble partida
- ✅ Libro mayor
- ✅ Activos fijos
- ✅ Cuentas por pagar/cobrar
- ✅ Declaraciones SRI
- ✅ Reportes contables
- ✅ Sistema de auditoría

## 🔐 Roles y Permisos

- **admin**: Acceso completo al sistema
- **contador**: Gestión contable completa
- **auditor**: Solo lectura y reportes
- **interno**: Acceso limitado según permisos

## 📊 Cumplimiento Fiscal

- Formularios SRI 103, 104, RDEP
- Plan contable ecuatoriano
- Trazabilidad completa de transacciones
- Exportación de reportes fiscales











