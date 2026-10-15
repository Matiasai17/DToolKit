# -*- coding: utf-8 -*-
"""
ATAJO DE TECLADO GLOBAL (funciona aunque la app no tenga el foco).

Usa directamente la funcion RegisterHotKey de Windows a traves de ctypes, asi
no hace falta instalar ninguna libreria extra ni permisos de administrador.
Los mensajes WM_HOTKEY que manda Windows se leen con un filtro de eventos
nativos de Qt.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes

from PySide6.QtCore import QAbstractNativeEventFilter, QCoreApplication

# Constantes de la API de Windows.
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000
WM_HOTKEY = 0x0312

_ID_ATAJO = 1

# Nombre de tecla -> codigo virtual de Windows.
_TECLAS: dict[str, int] = {
    "space": 0x20, "espacio": 0x20,
    "enter": 0x0D, "return": 0x0D,
    "tab": 0x09, "esc": 0x1B, "escape": 0x1B,
    "backspace": 0x08, "insert": 0x2D, "delete": 0x2E, "del": 0x2E,
    "home": 0x24, "end": 0x23, "pageup": 0x21, "pagedown": 0x22,
    "left": 0x25, "up": 0x26, "right": 0x27, "down": 0x28,
    "printscreen": 0x2C, "imprpant": 0x2C,
    "+": 0xBB, "-": 0xBD, ",": 0xBC, ".": 0xBE,
}
for _i in range(10):                      # 0-9
    _TECLAS[str(_i)] = 0x30 + _i
for _c in range(ord("a"), ord("z") + 1):  # a-z
    _TECLAS[chr(_c)] = 0x41 + (_c - ord("a"))
for _f in range(1, 13):                   # F1-F12
    _TECLAS[f"f{_f}"] = 0x70 + (_f - 1)


def traducir(atajo: str) -> tuple[int, int] | None:
    """Convierte "Ctrl+Shift+Space" en (modificadores, tecla) para Windows."""
    mods = 0
    tecla = None
    for parte in atajo.replace(" ", "").split("+"):
        if not parte:
            continue
        p = parte.lower()
        if p in ("ctrl", "control"):
            mods |= MOD_CONTROL
        elif p in ("shift", "mayus"):
            mods |= MOD_SHIFT
        elif p == "alt":
            mods |= MOD_ALT
        elif p in ("win", "meta", "super"):
            mods |= MOD_WIN
        else:
            tecla = _TECLAS.get(p)
            if tecla is None:
                return None
    if tecla is None or mods == 0:
        # Sin modificadores el atajo robaria la tecla a todo el sistema.
        return None
    return mods | MOD_NOREPEAT, tecla


class _Filtro(QAbstractNativeEventFilter):
    """Escucha los mensajes de Windows y detecta WM_HOTKEY."""

    def __init__(self, al_activarse) -> None:  # noqa: ANN001
        super().__init__()
        self._al_activarse = al_activarse

    def nativeEventFilter(self, tipo, mensaje):  # noqa: N802, ANN001
        if tipo == "windows_generic_MSG":
            msg = wintypes.MSG.from_address(int(mensaje))
            if msg.message == WM_HOTKEY and msg.wParam == _ID_ATAJO:
                self._al_activarse()
                return True, 0
        return False, 0


class AtajoGlobal:
    """Registra y des-registra el atajo. Avisa si la combinacion esta ocupada."""

    def __init__(self, al_activarse) -> None:  # noqa: ANN001
        self._al_activarse = al_activarse
        self._registrado = False
        self._filtro = _Filtro(al_activarse)
        QCoreApplication.instance().installNativeEventFilter(self._filtro)

    def aplicar(self, atajo: str) -> bool:
        """Deja activo solo este atajo. Devuelve False si no se pudo registrar."""
        self.quitar()
        if not atajo:
            return True
        combinacion = traducir(atajo)
        if combinacion is None:
            return False
        mods, tecla = combinacion
        ok = bool(ctypes.windll.user32.RegisterHotKey(None, _ID_ATAJO, mods, tecla))
        self._registrado = ok
        return ok

    def quitar(self) -> None:
        if self._registrado:
            ctypes.windll.user32.UnregisterHotKey(None, _ID_ATAJO)
            self._registrado = False
