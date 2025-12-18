@echo off
REM Frontend Server Launcher for Arteterapia

echo ========================================
echo   Arteterapia Frontend Server
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo Por favor instala Python desde https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

echo Iniciando servidor HTTP en puerto 8000...
echo.
echo Abre tu navegador en:
echo   http://localhost:8000/demo.html
echo   o
echo   http://localhost:8000/index.html
echo.
echo Presiona Ctrl+C para detener el servidor
echo ========================================
echo.

REM Start Python HTTP server
cd /d "%SCRIPT_DIR%"
python -m http.server 8000
