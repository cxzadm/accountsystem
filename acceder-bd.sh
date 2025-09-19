#!/bin/bash

echo "========================================"
echo "   ACCESO A LA BASE DE DATOS MONGODB"
echo "========================================"
echo

echo "1. VERIFICANDO DOCKER..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado o no está en el PATH"
    echo "💡 Instala Docker Desktop desde: https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo "✅ Docker está instalado"
echo

echo "2. VERIFICANDO CONTENEDOR MONGODB..."
docker ps -a --filter name=mongodb-sistema-contable --format "table {{.Names}}\t{{.Status}}"

echo
echo "3. INICIANDO MONGODB..."
docker start mongodb-sistema-contable 2>/dev/null || docker run -d --name mongodb-sistema-contable -p 27017:27017 mongo:latest

echo
echo "4. VERIFICANDO CONEXIÓN..."
sleep 3
if docker exec mongodb-sistema-contable mongosh --eval "db.runCommand('ping')" &>/dev/null; then
    echo "✅ MongoDB está ejecutándose correctamente"
else
    echo "⚠️  MongoDB está iniciando, espera unos segundos..."
fi

echo
echo "========================================"
echo "   OPCIONES DE ACCESO"
echo "========================================"
echo
echo "🌐 MONGODB COMPASS (Recomendado):"
echo "  1. Descarga: https://www.mongodb.com/products/compass"
echo "  2. URL: mongodb://localhost:27017"
echo "  3. Base de datos: sistema_contable_ec"
echo
echo "💻 MONGODB SHELL:"
echo "  1. Instala: https://www.mongodb.com/try/download/shell"
echo "  2. Ejecuta: mongosh mongodb://localhost:27017"
echo "  3. Cambia BD: use sistema_contable_ec"
echo
echo "🐳 DOCKER SHELL:"
echo "  docker exec -it mongodb-sistema-contable mongosh"
echo
echo "========================================"
echo "   COLECCIONES DISPONIBLES"
echo "========================================"
echo
echo "📊 Colecciones en sistema_contable_ec:"
echo "  • users          - Usuarios del sistema"
echo "  • companies      - Empresas registradas"
echo "  • accounts       - Plan de cuentas contables"
echo "  • journal_entries - Asientos contables"
echo "  • audit_logs     - Registros de auditoría"
echo









