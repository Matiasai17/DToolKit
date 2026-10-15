# -*- coding: utf-8 -*-
"""
Iniciar con Windows.

Escribe (o borra) un valor en
HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run
Es el mecanismo estandar y no necesita permisos de administrador: solo afecta
al usuario actual y tambien se puede desactivar desde el Administrador de
tareas, pestana "Inicio".
"""

from __future__ import annotations

import sys
import winreg
from pathlib import Path

from .. import APP_NOMBRE

_CLAVE = r"Software\Microsoft\Windows\CurrentVersion\Run"


def _comando() -> str:
    """El comando que Windows ejecuta al iniciar sesion."""
    if getattr(sys, "frozen", False):
        # Corriendo como .exe empaquetado: se llama a si mismo.
        return f'"{Path(sys.executable)}"'
    # Corriendo desde el codigo: pythonw.exe (sin ventana negra) + ejecutar.py
    exe = Path(sys.executable)
    sin_consola = exe.with_name("pythonw.exe")
    interprete = sin_consola if sin_consola.exists() else exe
    guion = Path(__file__).resolve().parents[2] / "ejecutar.py"
    return f'"{interprete}" "{guion}"'


def esta_activo() -> bool:
    """True si la app ya figura en el inicio de Windows."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _CLAVE) as clave:
            winreg.QueryValueEx(clave, APP_NOMBRE)
        return True
    except OSError:
        return False


def activar() -> bool:
    """Agrega la app al inicio de Windows. Devuelve True si salio bien."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _CLAVE, 0,
                            winreg.KEY_SET_VALUE) as clave:
            winreg.SetValueEx(clave, APP_NOMBRE, 0, winreg.REG_SZ, _comando())
        return True
    except OSError:
        return False


def desactivar() -> bool:
    """Quita la app del inicio de Windows."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _CLAVE, 0,
                            winreg.KEY_SET_VALUE) as clave:
            winreg.DeleteValue(clave, APP_NOMBRE)
        return True
    except FileNotFoundError:
        return True
    except OSError:
        return False


def aplicar(activado: bool) -> bool:
    """Sincroniza el registro con la preferencia del usuario."""
    return activar() if activado else desactivar()
