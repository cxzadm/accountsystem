#!/bin/bash
# Script para hacer ejecutables los scripts de Python

echo "🔧 Configurando permisos de ejecución para scripts..."

# Hacer ejecutables los scripts de Python
chmod +x import_initial_data.py
chmod +x quick_import.py
chmod +x setup_initial_data.py

echo "✅ Scripts configurados como ejecutables:"
echo "   📄 import_initial_data.py - Importador completo con interfaz"
echo "   ⚡ quick_import.py - Importación rápida"
echo "   🏗️  setup_initial_data.py - Configuración inicial completa"

echo ""
echo "🚀 Uso de los scripts:"
echo ""
echo "1. Importación completa (recomendado para primera vez):"
echo "   python scripts/import_initial_data.py"
echo ""
echo "2. Importación rápida:"
echo "   python scripts/quick_import.py backup_sistema_contable_2025-09-30.json"
echo ""
echo "3. Configuración inicial completa:"
echo "   python scripts/setup_initial_data.py"
echo ""
echo "4. Importación con parámetros específicos:"
echo "   python scripts/import_initial_data.py --file backup.json --mode replace"


