# -*- coding: utf-8 -*-
"""Ubicacion de los archivos de la app (funciona igual corriendo el .py o el .exe)."""

from __future__ import annotations

import sys
from pathlib import Path


def carpeta_recursos() -> Path:
    """Carpeta 'recursos'. PyInstaller la descomprime en sys._MEIPASS."""
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return Path(base) / "recursos"
    return Path(__file__).resolve().parent.parent / "recursos"


def ruta_icono(nombre: str) -> Path:
    return carpeta_recursos() / "iconos" / nombre
