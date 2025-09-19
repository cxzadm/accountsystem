# 📊 Gestión de Saldos Iniciales - Sistema Contable

## 🎯 Descripción

Esta funcionalidad permite gestionar los saldos iniciales del plan de cuentas desde la administración de empresas. Los usuarios pueden:

- ✅ Visualizar todas las cuentas contables con sus saldos iniciales
- ✅ Editar saldos iniciales directamente en la interfaz
- ✅ Exportar el plan de cuentas a Excel
- ✅ Importar saldos iniciales desde archivos Excel
- ✅ Validar que el plan esté balanceado (débitos = créditos)

## 🚀 Cómo acceder

1. **Navegar a Administración → Gestión de Empresas**
2. **Seleccionar una empresa**
3. **Hacer clic en el botón "Saldos Iniciales" (ícono de calculadora)**
4. **Se abrirá la interfaz de gestión de saldos iniciales**

## 📋 Funcionalidades principales

### 🔍 **Filtros y búsqueda**
- **Buscar por código o nombre** de cuenta
- **Filtrar por tipo** de cuenta (activo, pasivo, patrimonio, etc.)
- **Mostrar solo cuentas con saldos** o sin saldos
- **Paginación** para manejar grandes volúmenes de datos

### ✏️ **Edición de saldos**
- **Edición directa** en la tabla
- **Validación en tiempo real** de los totales
- **Indicador visual** de cuentas modificadas
- **Botón para limpiar saldos** de una cuenta específica

### 📊 **Resumen de saldos**
- **Total de débitos** y créditos
- **Diferencia** entre débitos y créditos
- **Indicador visual** si el plan está balanceado
- **Contador** de cuentas mostradas

### 📤 **Exportación a Excel**
- **Formato profesional** con encabezados formateados
- **Columnas**: Código, Cuenta, Tipo, Naturaleza, Saldo Débito, Saldo Crédito
- **Formato de moneda** automático
- **Nombre de archivo** con fecha y empresa

### 📥 **Importación desde Excel**
- **Vista previa** de los datos antes de importar
- **Validación** de formato y datos
- **Reporte de errores** detallado
- **Actualización masiva** de saldos

## 📁 Estructura del archivo Excel

### Columnas requeridas:
| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| `Código` | Código de la cuenta | `1101` |
| `Cuenta` | Nombre de la cuenta | `CAJA` |
| `Tipo` | Tipo de cuenta | `activo`, `pasivo`, `patrimonio`, `ingresos`, `gastos`, `costos` |
| `Naturaleza` | Naturaleza de la cuenta | `deudora`, `acreedora` |
| `Saldo Débito` | Saldo inicial débito | `5000.00` |
| `Saldo Crédito` | Saldo inicial crédito | `0.00` |

### Ejemplo de datos:
```
Código | Cuenta | Tipo | Naturaleza | Saldo Débito | Saldo Crédito
1101   | CAJA   | activo | deudora   | 5000.00     | 0.00
1102   | BANCOS | activo | deudora   | 25000.00    | 0.00
2101   | CUENTAS POR PAGAR | pasivo | acreedora | 0.00 | 12000.00
3101   | CAPITAL SOCIAL | patrimonio | acreedora | 0.00 | 100000.00
```

## 🔧 Instalación y configuración

### Backend
Los endpoints ya están implementados en `/backend/app/routes/accounts.py`:

- `GET /accounts/export-chart` - Exportar plan de cuentas
- `POST /accounts/import-initial-balances` - Importar saldos iniciales
- `PUT /accounts/initial-balances` - Actualizar saldos iniciales

### Frontend
El componente está en `/frontend/src/views/companies/InitialBalances.vue`

### Dependencias
```bash
# Frontend
npm install xlsx

# Backend (ya incluidas)
pip install pandas openpyxl
```

## 📝 Plan de cuentas de ejemplo

Se ha creado un plan de cuentas de ejemplo con las siguientes características:

### Estructura básica:
- **Activos**: Caja, Bancos, Cuentas por cobrar, Inventarios, Inmuebles
- **Pasivos**: Cuentas por pagar, Impuestos, Obligaciones financieras
- **Patrimonio**: Capital social, Reservas, Utilidades acumuladas
- **Ingresos**: Ventas, Servicios, Ingresos financieros
- **Gastos**: Gastos de ventas, administrativos, financieros
- **Costos**: Costo de ventas, Costo de producción

### Saldos iniciales incluidos:
- **Total Débito**: $210,000.00
- **Total Crédito**: $235,000.00
- **Diferencia**: $25,000.00 (no balanceado intencionalmente para demostración)

## 🎮 Cómo usar

### 1. **Crear empresa de ejemplo**
```bash
cd backend
python scripts/create_sample_chart.py
```

### 2. **Generar archivo Excel de plantilla**
```bash
python scripts/create_excel_template.py
```

### 3. **Acceder a la interfaz**
1. Iniciar el servidor backend
2. Iniciar el frontend
3. Navegar a Administración → Empresas
4. Hacer clic en "Saldos Iniciales" para la empresa de ejemplo

### 4. **Probar funcionalidades**
- ✅ Ver el plan de cuentas con saldos iniciales
- ✅ Exportar a Excel
- ✅ Modificar saldos en la interfaz
- ✅ Importar desde Excel
- ✅ Validar balance

## 🔒 Permisos requeridos

- `accounts:read` - Para ver cuentas y exportar
- `accounts:update` - Para modificar saldos iniciales
- `companies:read` - Para acceder a empresas

## 🐛 Solución de problemas

### Error: "No tienes acceso a esta empresa"
- Verificar que el usuario tenga permisos para la empresa
- Asegurar que la empresa esté asignada al usuario

### Error: "El asiento no está balanceado"
- Verificar que el total de débitos sea igual al total de créditos
- Revisar que no haya errores de tipeo en los montos

### Error al importar Excel
- Verificar que las columnas tengan los nombres correctos
- Asegurar que los valores numéricos estén en formato correcto
- Revisar que los códigos de cuenta existan en el sistema

## 📈 Próximas mejoras

- [ ] Validación de saldos por tipo de cuenta
- [ ] Historial de cambios en saldos iniciales
- [ ] Generación automática de asientos de apertura
- [ ] Reportes de balance de apertura
- [ ] Importación masiva desde múltiples archivos

## 📞 Soporte

Para soporte técnico o reportar bugs, contactar al equipo de desarrollo.

---

**Desarrollado con ❤️ para el Sistema Contable**
