# -*- coding: utf-8 -*-
"""
Carga los iconos SVG y los pinta con el color del tema.

Asi los SVG pueden ser negros o de cualquier color: la app los recolorea sola
usando COLOR_ICONO / COLOR_ICONO_HOVER de tema.py.
"""

from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

from .. import tema
from .recursos import ruta_icono

# Cache para no releer el SVG cada vez que se abre la barra.
_cache: dict[tuple, QIcon] = {}


def _pixmap_svg(nombre: str, lado: int, color: str, dpr: float) -> QPixmap:
    px = QPixmap(QSize(int(lado * dpr), int(lado * dpr)))
    px.setDevicePixelRatio(dpr)
    px.fill(Qt.transparent)
    ruta = ruta_icono(nombre)
    if ruta.exists():
        pintor = QPainter(px)
        pintor.setRenderHint(QPainter.Antialiasing, True)
        # Ojo: al tener el pixmap un devicePixelRatio, el pintor ya trabaja en
        # coordenadas logicas. Hay que dibujar en `lado`, no en `lado * dpr`,
        # o el dibujo sale al doble de tamano y recortado.
        QSvgRenderer(str(ruta)).render(pintor, QRectF(0, 0, lado, lado))
        # Reemplaza el color original del dibujo por el del tema,
        # conservando la transparencia.
        pintor.setCompositionMode(QPainter.CompositionMode_SourceIn)
        pintor.fillRect(px.rect(), QColor(color))
        pintor.end()
    return px


def icono(nombre: str, lado: int | None = None, dpr: float = 2.0) -> QIcon:
    """Devuelve un QIcon con el estado normal y el de hover ya coloreados."""
    lado = lado or tema.TAMANO_ICONO
    clave = (nombre, lado, dpr)
    if clave not in _cache:
        ico = QIcon()
        ico.addPixmap(_pixmap_svg(nombre, lado, tema.COLOR_ICONO, dpr), QIcon.Normal)
        ico.addPixmap(_pixmap_svg(nombre, lado, tema.COLOR_ICONO_HOVER, dpr), QIcon.Active)
        ico.addPixmap(_pixmap_svg(nombre, lado, tema.COLOR_ICONO_HOVER, dpr), QIcon.Selected)
        _cache[clave] = ico
    return _cache[clave]


def icono_app() -> QIcon:
    """Icono de la bandeja del sistema: varios tamanos para que se vea nitido."""
    ico = QIcon()
    for lado in (16, 20, 24, 32, 48, 64, 256):
        ico.addPixmap(_pixmap_svg("app.svg", lado, tema.COLOR_ICONO, 1.0))
    return ico
