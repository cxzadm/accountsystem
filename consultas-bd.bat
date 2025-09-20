@echo off
echo ========================================
echo    CONSULTAS RÁPIDAS A LA BASE DE DATOS
echo ========================================
echo.

:menu
echo Selecciona una opción:
echo 1. Ver todos los usuarios
echo 2. Ver todas las empresas
echo 3. Ver plan de cuentas
echo 4. Ver asientos contables
echo 5. Ver logs de auditoría
echo 6. Conectar a MongoDB Shell
echo 7. Salir
echo.
set /p choice="Ingresa tu opción (1-7): "

if "%choice%"=="1" goto usuarios
if "%choice%"=="2" goto empresas
if "%choice%"=="3" goto cuentas
if "%choice%"=="4" goto asientos
if "%choice%"=="5" goto auditoria
if "%choice%"=="6" goto shell
if "%choice%"=="7" goto salir
goto menu

:usuarios
echo.
echo ========================================
echo    USUARIOS DEL SISTEMA
echo ========================================
docker exec mongodb-sistema-contable mongosh sistema_contable_ec --eval "db.users.find().pretty()"
echo.
pause
goto menu

:empresas
echo.
echo ========================================
echo    EMPRESAS REGISTRADAS
echo ========================================
docker exec mongodb-sistema-contable mongosh sistema_contable_ec --eval "db.companies.find().pretty()"
echo.
pause
goto menu

:cuentas
echo.
echo ========================================
echo    PLAN DE CUENTAS CONTABLES
echo ========================================
docker exec mongodb-sistema-contable mongosh sistema_contable_ec --eval "db.accounts.find().pretty()"
echo.
pause
goto menu

:asientos
echo.
echo ========================================
echo    ASIENTOS CONTABLES
echo ========================================
docker exec mongodb-sistema-contable mongosh sistema_contable_ec --eval "db.journal_entries.find().pretty()"
echo.
pause
goto menu

:auditoria
echo.
echo ========================================
echo    LOGS DE AUDITORÍA
echo ========================================
docker exec mongodb-sistema-contable mongosh sistema_contable_ec --eval "db.audit_logs.find().sort({timestamp: -1}).limit(10).pretty()"
echo.
pause
goto menu

:shell
echo.
echo ========================================
echo    CONECTANDO A MONGODB SHELL
echo ========================================
echo Comandos útiles:
echo   show dbs                    - Ver bases de datos
echo   use sistema_contable_ec     - Cambiar a la BD
echo   show collections           - Ver colecciones
echo   db.users.find()            - Ver usuarios
echo   exit                       - Salir
echo.
docker exec -it mongodb-sistema-contable mongosh
goto menu

:salir
echo.
echo ¡Hasta luego!
exit /b 0










