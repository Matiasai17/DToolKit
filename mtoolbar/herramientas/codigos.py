# -*- coding: utf-8 -*-
"""
HERRAMIENTA 2: Lector de QR y codigos de barras.

Dos modos:
  - Seleccionar un area de la pantalla (el modo principal).
  - Cargar una imagen del disco (click derecho en el boton, o menu de la bandeja).

Decodifica con zxing-cpp, que soporta QR, Micro QR, DataMatrix, Aztec, PDF417,
EAN-13, EAN-8, UPC-A, UPC-E, Code 128, Code 39, Code 93, ITF, Codabar y DataBar.
"""

from __future__ import annotations

import zxingcpp
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap

from ..nucleo.herramienta import Herramienta, registrar
from ..ventanas.resultado import VentanaResultado

# Nombres lindos para mostrar en la ventana de resultado.
NOMBRES_FORMATO = {
    "QRCode": "Codigo QR",
    "MicroQRCode": "Micro QR",
    "RMQRCode": "rMQR",
    "DataMatrix": "DataMatrix",
    "Aztec": "Aztec",
    "PDF417": "PDF417",
    "EAN13": "EAN-13",
    "EAN8": "EAN-8",
    "UPCA": "UPC-A",
    "UPCE": "UPC-E",
    "Code128": "Code 128",
    "Code39": "Code 39",
    "Code93": "Code 93",
    "Codabar": "Codabar",
    "ITF": "ITF",
    "DataBar": "DataBar",
    "MaxiCode": "MaxiCode",
}


def _decodificar(imagen: QImage) -> list:
    """Busca codigos en la imagen. Devuelve la lista de resultados de zxing-cpp."""
    if imagen.isNull():
        return []
    # Las imagenes muy chicas se agrandan sin suavizado: ayuda a leer codigos
    # de pocos pixeles (un QR chiquito en una pagina web, por ejemplo).
    lado_menor = min(imagen.width(), imagen.height())
    if 0 < lado_menor < 180:
        factor = max(2, 360 // lado_menor)
        imagen = imagen.scaled(
            imagen.width() * factor, imagen.height() * factor,
            Qt.KeepAspectRatio, Qt.FastTransformation,
        )
    gris = imagen.convertToFormat(QImage.Format_Grayscale8)
    try:
        return zxingcpp.read_barcodes(gris)
    except Exception:
        return []


def nombre_formato(resultado) -> str:  # noqa: ANN001
    crudo = getattr(resultado.format, "name", str(resultado.format))
    return NOMBRES_FORMATO.get(crudo, crudo)


@registrar
class LectorCodigos(Herramienta):
    id = "codigos"
    nombre = "Leer QR / codigo de barras"
    icono = "codigos.svg"
    atajo_local = "2"
    orden = 20

    def ejecutar(self, ctx) -> None:  # noqa: ANN001
        recorte: QPixmap | None = ctx.seleccionar_area()
        if recorte is None:
            return
        self._mostrar(ctx, recorte.toImage())

    def acciones_extra(self, ctx) -> list:  # noqa: ANN001
        return [("Leer desde una imagen...", lambda: self._desde_archivo(ctx))]

    # ------------------------------------------------------------------ interno
    def _desde_archivo(self, ctx) -> None:  # noqa: ANN001
        imagen = ctx.abrir_archivo_imagen("Elegir una imagen con el codigo")
        if imagen is not None:
            self._mostrar(ctx, imagen)

    def _mostrar(self, ctx, imagen: QImage) -> None:  # noqa: ANN001
        resultados = _decodificar(imagen)
        if not resultados:
            ctx.avisar("No se encontro ningun codigo")
            return
        VentanaResultado.abrir(ctx, resultados)
