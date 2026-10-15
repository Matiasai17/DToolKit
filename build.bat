@echo off
rem ===================================================================
rem  MToolBar - genera el ejecutable portable  dist\MToolBar.exe
rem  Doble click y esperar (la primera vez tarda varios minutos).
rem
rem  La receta del empaquetado esta en MToolBar.spec: ahi se decide que
rem  partes de Qt entran y cuales no, y si sale un solo .exe o una carpeta.
rem ===================================================================
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo  Falta el entorno. Corre primero run.bat una vez.
    pause
    exit /b 1
)

echo.
echo  [1/4] Instalando PyInstaller si hace falta...
".venv\Scripts\python.exe" -m pip install --upgrade pyinstaller
if errorlevel 1 goto error

echo.
echo  [2/4] Generando el icono del ejecutable desde app.svg...
".venv\Scripts\python.exe" "utiles\generar_ico.py"

echo.
echo  [3/4] Empaquetando (segun MToolBar.spec)...
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean "MToolBar.spec"
if errorlevel 1 goto error

echo.
echo  [4/4] Comprobando que el ejecutable funcione...
rem  start /wait es necesario: cmd no espera a un programa sin consola.
start "" /wait "dist\MToolBar.exe" --autoprueba
if errorlevel 1 goto autoprueba_mal
type "dist\autoprueba.txt"

echo.
echo  ======================================================
echo   Listo:  dist\MToolBar.exe
echo   Es portable: copialo a donde quieras y listo.
echo  ======================================================
echo.
pause
exit /b 0

:autoprueba_mal
echo.
echo  OJO: el ejecutable se genero pero la autoprueba fallo.
echo  El detalle esta en dist\autoprueba.txt
echo.
type "dist\autoprueba.txt"
pause
exit /b 1

:error
echo.
echo  Hubo un error en el empaquetado. Mira los mensajes de arriba.
echo.
pause
exit /b 1
