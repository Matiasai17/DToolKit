# -*- coding: utf-8 -*-
"""
Genera el icono del .exe (app.ico) a partir de app.svg y los colores del tema.

Lo corre build.bat solo, asi el icono del ejecutable siempre coincide con el
diseno. Tambien lo podes correr a mano:

    .venv\\Scripts\\python utiles\\generar_ico.py

A diferencia del icono de la bandeja (que es solo el dibujo, sin fondo), el del
.exe lleva un cuadrado redondeado de fondo para que se vea en el explorador de
archivos tanto en tema claro como oscuro.
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from PySide6.QtCore import QRectF, Qt  # noqa: E402
from PySide6.QtGui import QColor, QGuiApplication, QImage, QPainter  # noqa: E402
from PySide6.QtSvg import QSvgRenderer  # noqa: E402

from mtoolbar import tema  # noqa: E402

# Fondo del icono del ejecutable (podes cambiarlo por cualquier color).
COLOR_FONDO_ICO = "#FF202124"
MARGEN = 0.17        # aire alrededor del dibujo, como porcentaje del lado
RADIO = 0.22         # redondeo del cuadrado, como porcentaje del lado
LADOS = (16, 20, 24, 32, 48, 64, 128, 256)


def _capa(lado: int) -> QImage:
    img = QImage(lado, lado, QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing, True)

    # Fondo redondeado
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(COLOR_FONDO_ICO))
    p.drawRoundedRect(QRectF(0, 0, lado, lado), lado * RADIO, lado * RADIO)

    # Dibujo del SVG, centrado
    svg = RAIZ / "mtoolbar" / "recursos" / "iconos" / "app.svg"
    dentro = QRectF(lado * MARGEN, lado * MARGEN, lado * (1 - 2 * MARGEN),
                    lado * (1 - 2 * MARGEN))
    capa = QImage(lado, lado, QImage.Format_ARGB32)
    capa.fill(Qt.transparent)
    p2 = QPainter(capa)
    p2.setRenderHint(QPainter.Antialiasing, True)
    QSvgRenderer(str(svg)).render(p2, dentro)
    # Recolorea el dibujo con el color de icono del tema.
    p2.setCompositionMode(QPainter.CompositionMode_SourceIn)
    p2.fillRect(capa.rect(), QColor(tema.COLOR_ICONO))
    p2.end()

    p.drawImage(0, 0, capa)
    p.end()
    return img


def main() -> int:
    QGuiApplication([])
    destino = RAIZ / "mtoolbar" / "recursos" / "iconos" / "app.ico"
    # El formato ICO de Qt guarda una sola imagen; se usa la mas grande, que
    # Windows reescala bien para todos los tamanos.
    grande = _capa(256)
    if not grande.save(str(destino), "ICO"):
        print("No se pudo escribir", destino)
        return 1
    print("Icono generado:", destino)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
