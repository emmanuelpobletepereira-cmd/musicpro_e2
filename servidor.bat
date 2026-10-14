@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo No se encontro el entorno virtual .venv.
    echo Consulta la preparacion del entorno en README.md.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" manage.py runserver %*
if errorlevel 1 pause
