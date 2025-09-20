@echo off
echo ========================================
echo  Sistema Contable  Accescont Ecuador - Inicio Rapido
echo ========================================
echo.

echo [1/4] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado
    pause
    exit /b 1
)
echo ✓ Python encontrado

echo.
echo [2/4] Verificando Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js no esta instalado
    pause
    exit /b 1
)
echo ✓ Node.js encontrado

echo.
echo [3/4] Iniciando Backend...
cd backend
if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
)

call venv\Scripts\activate
pip install -r requirements.txt >nul 2>&1

echo Iniciando servidor backend en puerto 8000...
start "Backend" cmd /k "call venv\Scripts\activate && python scripts\run_server.py"

echo.
echo [4/4] Iniciando Frontend...
cd ..\frontend
if not exist "node_modules" (
    echo Instalando dependencias...
    npm install
)

echo Iniciando servidor frontend en puerto 5173...
start "Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo  Sistema iniciado exitosamente!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo Docs:     http://localhost:8000/docs
echo.
echo Credenciales:
echo - Admin: admin / admin123
echo - Contador: contador / contador123
echo.
echo Presiona cualquier tecla para cerrar...
pause >nul











