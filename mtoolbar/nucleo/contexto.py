# -*- coding: utf-8 -*-
"""
EL CONTEXTO: lo que recibe cada herramienta cuando se ejecuta.

Una herramienta nunca habla directamente con la barra, la bandeja ni el
portapapeles: todo pasa por aca. Asi se pueden agregar herramientas nuevas sin
tocar ni una linea del resto de la app.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices, QGuiApplication, QImage, QPixmap

from .. import APP_NOMBRE
from . import aviso as _aviso
from . import pantalla as _pantalla
from . import selector as _selector


class Contexto:
    """Caja de herramientas que la app le presta a cada modulo."""

    def __init__(self, config, app) -> None:  # noqa: ANN001
        self.config = config
        self.app = app          # la aplicacion (para cerrar la barra, abrir ajustes...)

    # ----------------------------------------------------------------- pantalla
    def seleccionar_area(self) -> QPixmap | None:
        """Abre el overlay y devuelve lo seleccionado (None si se cancelo)."""
        return _selector.seleccionar_area()

    def capturar_pantalla_completa(self) -> QPixmap | None:
        """Captura el monitor donde esta el mouse, sin pedir seleccion."""
        congelado = _pantalla.congelar()
        from PySide6.QtGui import QCursor
        foto = congelado.pantalla_en(QCursor.pos())
        return congelado.recortar(foto.geometria) if foto else None

    # -------------------------------------------------------------- portapapeles
    def copiar_imagen(self, pixmap: QPixmap) -> None:
        QGuiApplication.clipboard().setPixmap(pixmap)

    def copiar_texto(self, texto: str) -> None:
        QGuiApplication.clipboard().setText(texto)

    def leer_texto(self) -> str:
        """El texto que hay en el portapapeles ("" si hay una imagen o nada)."""
        return QGuiApplication.clipboard().text()

    # -------------------------------------------------------------------- avisos
    def avisar(self, texto: str) -> None:
        _aviso.avisar(texto)

    # ------------------------------------------------------------------ archivos
    def guardar_png(self, pixmap: QPixmap, prefijo: str = "Captura") -> Path | None:
        """Guarda el PNG en la carpeta configurada con fecha y hora en el nombre."""
        try:
            carpeta = self.config.asegurar_carpeta()
        except OSError:
            self.avisar("No se pudo crear la carpeta de guardado")
            return None
        sello = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        ruta = carpeta / f"{APP_NOMBRE}_{prefijo}_{sello}.png"
        return ruta if pixmap.save(str(ruta), "PNG") else None

    def abrir_archivo_imagen(self, titulo: str = "Elegir imagen") -> QImage | None:
        """Dialogo para cargar una imagen del disco."""
        from PySide6.QtWidgets import QFileDialog

        ruta, _ = QFileDialog.getOpenFileName(
            None, titulo, str(Path.home()),
            "Imagenes (*.png *.jpg *.jpeg *.bmp *.gif *.webp *.tif *.tiff);;Todos los archivos (*)",
        )
        if not ruta:
            return None
        imagen = QImage(ruta)
        if imagen.isNull():
            self.avisar("No se pudo abrir esa imagen")
            return None
        return imagen

    def abrir_url(self, url: str) -> None:
        QDesktopServices.openUrl(QUrl(url))

    def abrir_carpeta(self, ruta: Path) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(ruta)))

    # --------------------------------------------------------------------- barra
    def cerrar_barra(self) -> None:
        self.app.ocultar_barra()

    def abrir_ajustes(self) -> None:
        self.app.abrir_ajustes()
