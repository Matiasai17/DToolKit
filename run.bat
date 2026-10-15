@echo off
rem ===================================================================
rem  MToolBar - doble click para ejecutar la app.
rem  La primera vez prepara el entorno (tarda unos minutos); despues
rem  arranca en un segundo y aparece el icono en la bandeja del sistema.
rem ===================================================================
cd /d "%~dp0"

if not exist ".venv\Scripts\pythonw.exe" (
    echo.
    echo  Preparando el entorno por primera vez. Esto tarda unos minutos...
    echo.
    py -3 -m venv .venv
    if errorlevel 1 goto sin_python
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto error_pip
    echo.
    echo  Listo.
)

rem pythonw.exe = sin ventana negra de consola.
start "" ".venv\Scripts\pythonw.exe" "ejecutar.py"
exit /b 0

:sin_python
echo.
echo  No se encontro Python. Instalalo desde https://www.python.org/downloads/
echo  (marca la opcion "Add python.exe to PATH") y volve a correr este archivo.
echo.
pause
exit /b 1

:error_pip
echo.
echo  Fallo la instalacion de las dependencias. Revisa tu conexion a internet.
echo.
pause
exit /b 1
