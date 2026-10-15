# -*- mode: python ; coding: utf-8 -*-
"""
Receta de empaquetado de MToolBar.

PyInstaller, por las dudas, mete TODO Qt: el motor web, Qt Quick, OpenGL por
software, OpenSSL, los traductores... unos 150 MB de los cuales la app usa una
fraccion. Este archivo deja solo lo necesario.

Se usa asi (lo hace build.bat solo):

    .venv\\Scripts\\python -m PyInstaller --noconfirm MToolBar.spec

Si alguna vez agregas una herramienta que necesite un modulo de Qt nuevo
(por ejemplo QtMultimedia para la camara), sumalo a MODULOS_QT y a
BIBLIOTECAS_QT de aca abajo, y corre la autoprueba para confirmar:

    dist\\MToolBar.exe --autoprueba
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# OPCIONES
# ---------------------------------------------------------------------------
# True  = un unico archivo .exe (portable, arranca 1-2 s mas lento).
# False = una carpeta dist\\MToolBar\\ (arranca al instante).
UN_SOLO_ARCHIVO = True

RAIZ = Path(SPECPATH)  # noqa: F821  (SPECPATH lo define PyInstaller)

# Modulos de Python de Qt que la app importa de verdad.
MODULOS_QT = {"QtCore", "QtGui", "QtWidgets", "QtSvg"}

# Las DLL de Qt que corresponden a esos modulos (en minuscula, sin extension).
BIBLIOTECAS_QT = {"qt6core", "qt6gui", "qt6widgets", "qt6svg"}

# Plugins de Qt que si o si hacen falta:
#   platforms      -> sin esto Qt no abre ninguna ventana
#   styles         -> el aspecto nativo de Windows 11
#   imageformats   -> abrir/guardar PNG, JPG, ICO, etc.
#   iconengines    -> iconos SVG
PLUGINS_QT = {"platforms", "styles", "imageformats", "iconengines"}

# Cosas pesadas que no usamos nunca.
BASURA = (
    "opengl32sw.dll",        # OpenGL por software: 20 MB
    "d3dcompiler_47.dll",    # shaders de Direct3D, solo para Qt Quick
    # OpenSSL que trae Qt (termina en "-x64.dll", solo lo usa QtNetwork).
    # OJO: el de Python (libcrypto-3.dll y libssl-3.dll, sin "-x64") SI hace
    # falta: lo usa el traductor para HTTPS. La autoprueba lo verifica.
    "libcrypto-3-x64.dll", "libssl-3-x64.dll",
    "libegl", "libglesv2",   # ANGLE
    "qdirect2d.dll",         # plataforma alternativa: Qt usa qwindows.dll
)


def _sobra(destino: str) -> bool:
    """True si este archivo se puede dejar afuera del paquete."""
    ruta = destino.replace("\\", "/")
    partes = ruta.split("/")
    nombre = partes[-1].lower()

    if any(nombre.startswith(b) for b in BASURA):
        return True

    if "PySide6" not in partes and "pyside6" not in [p.lower() for p in partes]:
        return False

    # Las DLL de Qt que no estan en la lista blanca.
    if nombre.startswith("qt6") and nombre.endswith(".dll"):
        return nombre[:-4] not in BIBLIOTECAS_QT

    # Los modulos de Python de Qt que no usamos (QtQuick.pyd, QtPdf.pyd, ...).
    if nombre.startswith("qt") and nombre.endswith(".pyd"):
        return partes[-1].split(".")[0] not in MODULOS_QT

    # Plugins de Qt fuera de las categorias necesarias.
    if "plugins" in partes:
        i = partes.index("plugins")
        if i + 1 < len(partes) and partes[i + 1] not in PLUGINS_QT:
            return True

    # Traducciones de Qt (la app esta en castellano, escrito a mano).
    if "translations" in partes:
        return True

    return False


a = Analysis(  # noqa: F821
    ["ejecutar.py"],
    pathex=[str(RAIZ)],
    binaries=[],
    datas=[(str(RAIZ / "mtoolbar" / "recursos"), "recursos")],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        # Modulos de Qt que no usamos (evita que entren por la puerta de atras).
        "PySide6.QtNetwork", "PySide6.QtQml", "PySide6.QtQuick",
        "PySide6.QtQuick3D", "PySide6.QtQuickWidgets", "PySide6.QtQuickControls2",
        "PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets",
        "PySide6.QtWebEngineQuick", "PySide6.QtWebChannel", "PySide6.QtWebSockets",
        "PySide6.QtMultimedia", "PySide6.QtMultimediaWidgets", "PySide6.QtPdf",
        "PySide6.QtPdfWidgets", "PySide6.QtCharts", "PySide6.QtDataVisualization",
        "PySide6.QtOpenGL", "PySide6.QtOpenGLWidgets", "PySide6.Qt3DCore",
        "PySide6.QtDesigner", "PySide6.QtUiTools", "PySide6.QtTest",
        "PySide6.QtSql", "PySide6.QtBluetooth", "PySide6.QtNfc",
        "PySide6.QtPositioning", "PySide6.QtSerialPort", "PySide6.QtSensors",
        "PySide6.QtTextToSpeech", "PySide6.QtSpatialAudio",
        "PySide6.QtRemoteObjects", "PySide6.QtScxml", "PySide6.QtStateMachine",
        "PySide6.QtHelp", "PySide6.QtNetworkAuth", "PySide6.QtVirtualKeyboard",
        "PySide6.QtPrintSupport", "PySide6.QtXml", "PySide6.QtConcurrent",
        "PySide6.QtDBus", "PySide6.QtLocation", "PySide6.QtHttpServer",
        # Librerias de Python que la app no usa.
        # (ssl, http y email NO van aca: el traductor las necesita para HTTPS.)
        "numpy", "PIL", "tkinter", "unittest", "pydoc", "doctest",
        "xml", "xmlrpc", "sqlite3", "ftplib", "lib2to3",
        "pdb", "bdb", "multiprocessing", "asyncio",
        "curses", "distutils", "setuptools", "pip",
    ],
    noarchive=False,
    optimize=2,          # quita docstrings y asserts del bytecode
)

# --- el recorte -------------------------------------------------------------
antes = len(a.binaries) + len(a.datas)
a.binaries = [e for e in a.binaries if not _sobra(e[1])]
a.datas = [e for e in a.datas if not _sobra(e[1])]
print(f"[MToolBar] recorte: {antes} archivos -> {len(a.binaries) + len(a.datas)}")

pyz = PYZ(a.pure)  # noqa: F821

comunes = dict(
    name="MToolBar",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                # UPX comprime mas pero lo marcan los antivirus
    console=False,            # sin ventana negra
    disable_windowed_traceback=False,
    icon=str(RAIZ / "mtoolbar" / "recursos" / "iconos" / "app.ico"),
)

if UN_SOLO_ARCHIVO:
    exe = EXE(pyz, a.scripts, a.binaries, a.datas, [],  # noqa: F821
              runtime_tmpdir=None, **comunes)
else:
    exe = EXE(pyz, a.scripts, [], exclude_binaries=True, **comunes)  # noqa: F821
    coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False,  # noqa: F821
                   name="MToolBar")
