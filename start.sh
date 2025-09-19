#!/bin/bash

echo "========================================"
echo " Sistema Contable  Accescont Ecuador - Inicio Rapido"
echo "========================================"
echo

echo "[1/4] Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python no esta instalado"
    exit 1
fi
echo "✓ Python encontrado"

echo
echo "[2/4] Verificando Node.js..."
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js no esta instalado"
    exit 1
fi
echo "✓ Node.js encontrado"

echo
echo "[3/4] Iniciando Backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

echo "Iniciando servidor backend en puerto 8000..."
gnome-terminal --title="Backend" -- bash -c "source venv/bin/activate && python scripts/run_server.py; exec bash" &

echo
echo "[4/4] Iniciando Frontend..."
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo "Instalando dependencias..."
    npm install
fi

echo "Iniciando servidor frontend en puerto 5173..."
gnome-terminal --title="Frontend" -- bash -c "npm run dev; exec bash" &

echo
echo "========================================"
echo " Sistema iniciado exitosamente!"
echo "========================================"
echo
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "Docs:     http://localhost:8000/docs"
echo
echo "Credenciales:"
echo "- Admin: admin / admin123"
echo "- Contador: contador / contador123"
echo
echo "Presiona Enter para cerrar..."
read










