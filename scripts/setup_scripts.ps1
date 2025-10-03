# Script de PowerShell para configurar los scripts de Python
# Sistema Contable Ecuador

Write-Host "🔧 Configurando scripts de configuración inicial..." -ForegroundColor Green

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "scripts/import_initial_data.py")) {
    Write-Host "❌ Error: No se encontraron los scripts en la carpeta scripts/" -ForegroundColor Red
    Write-Host "   Asegúrate de ejecutar este script desde el directorio raíz del proyecto" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Scripts encontrados:" -ForegroundColor Green
Write-Host "   📄 import_initial_data.py - Importador completo con interfaz" -ForegroundColor Cyan
Write-Host "   ⚡ quick_import.py - Importación rápida" -ForegroundColor Cyan
Write-Host "   🏗️  setup_initial_data.py - Configuración inicial completa" -ForegroundColor Cyan

Write-Host ""
Write-Host "🚀 Guía de uso de los scripts:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Configuración inicial completa (recomendado para primera vez):" -ForegroundColor White
Write-Host "   python scripts/setup_initial_data.py" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Importación con interfaz interactiva:" -ForegroundColor White
Write-Host "   python scripts/import_initial_data.py" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Importación rápida:" -ForegroundColor White
Write-Host "   python scripts/quick_import.py backup_sistema_contable_2025-09-30.json" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Importación con parámetros específicos:" -ForegroundColor White
Write-Host "   python scripts/import_initial_data.py --file backup.json --mode replace" -ForegroundColor Gray

Write-Host ""
Write-Host "📋 Características de cada script:" -ForegroundColor Yellow
Write-Host ""
Write-Host "🏗️  setup_initial_data.py:" -ForegroundColor Cyan
Write-Host "   - Crea usuario administrador" -ForegroundColor Gray
Write-Host "   - Crea empresa de ejemplo" -ForegroundColor Gray
Write-Host "   - Configura plan de cuentas básico" -ForegroundColor Gray
Write-Host "   - Crea tipos de documentos" -ForegroundColor Gray
Write-Host "   - Importa archivos de backup" -ForegroundColor Gray
Write-Host "   - Verifica estado del sistema" -ForegroundColor Gray

Write-Host ""
Write-Host "📄 import_initial_data.py:" -ForegroundColor Cyan
Write-Host "   - Selección interactiva de archivos" -ForegroundColor Gray
Write-Host "   - Validación de estructura de backup" -ForegroundColor Gray
Write-Host "   - Múltiples modos de importación" -ForegroundColor Gray
Write-Host "   - Verificación de datos existentes" -ForegroundColor Gray
Write-Host "   - Soporte para diferentes formatos" -ForegroundColor Gray

Write-Host ""
Write-Host "⚡ quick_import.py:" -ForegroundColor Cyan
Write-Host "   - Importación directa sin interfaz" -ForegroundColor Gray
Write-Host "   - Ideal para automatización" -ForegroundColor Gray
Write-Host "   - Soporte para archivos JSON" -ForegroundColor Gray
Write-Host "   - Limpieza automática de datos existentes" -ForegroundColor Gray

Write-Host ""
Write-Host "📖 Para más información, consulta scripts/README.md" -ForegroundColor Green
Write-Host ""
Write-Host "🎉 Scripts configurados y listos para usar!" -ForegroundColor Green


