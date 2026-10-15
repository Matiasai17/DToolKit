# -*- coding: utf-8 -*-
"""
ARRANQUE DE LA APP.

Levanta Qt, el icono de la bandeja, el atajo global y la barra flotante, y se
queda esperando en segundo plano. No abre ninguna ventana al iniciar.

Para ejecutar:  python -m mtoolbar     (o doble click en run.bat)
"""

from __future__ import annotations

import sys

from PySide6.QtCore import QSharedMemory, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon

from . import APP_NOMBRE, tema
from .config import Config
from .nucleo import inicio_windows
from .nucleo.atajo import AtajoGlobal
from .nucleo.bandeja import Bandeja
from .nucleo.barra import Barra
from .nucleo.contexto import Contexto
from .nucleo.herramienta import Herramienta

# Importar el paquete de herramientas las registra en el REGISTRO.
from . import herramientas  # noqa: F401  (el import tiene efecto secundario)


class Aplicacion:
    """Une todas las piezas: bandeja + barra + atajo + preferencias."""

    def __init__(self, argv: list[str]) -> None:
        self.qapp = QApplication(argv)
        self.qapp.setApplicationName(APP_NOMBRE)
        self.qapp.setApplicationDisplayName(APP_NOMBRE)
        self.qapp.setOrganizationName(APP_NOMBRE)
        # Sin esto la app se cerraria al cerrar la ultima ventana.
        self.qapp.setQuitOnLastWindowClosed(False)
        self.qapp.setFont(QFont(tema.FUENTE, tema.TAMANO_TEXTO))
        self.qapp.setStyleSheet(tema.qss())

        self.config = Config()
        self.ctx = Contexto(self.config, self)
        self.barra = Barra(self.ctx)
        self.ventana_ajustes = None

        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(
                None, APP_NOMBRE,
                "Windows no esta mostrando la bandeja del sistema, asi que la app "
                "no tendria donde vivir."
            )
            raise SystemExit(1)

        self.bandeja = Bandeja(self)
        self.bandeja.show()

        self.atajo = AtajoGlobal(self.mostrar_barra)
        self.aplicar_atajo()

        # Mantiene el registro de inicio de Windows en sintonia con la
        # preferencia (por ejemplo si se movio el .exe de carpeta).
        if self.config.inicio_con_windows and not inicio_windows.esta_activo():
            inicio_windows.activar()

    # ------------------------------------------------------------------- barra
    def mostrar_barra(self) -> None:
        self.barra.mostrar()

    def ocultar_barra(self) -> None:
        self.barra.hide()

    def alternar_barra(self) -> None:
        if self.barra.isVisible():
            self.barra.hide()
        else:
            self.barra.mostrar()

    def ejecutar_herramienta(self, herramienta: Herramienta) -> None:
        """Usado desde el menu de la bandeja."""
        self.barra.hide()
        QTimer.singleShot(90, lambda: herramienta.ejecutar(self.ctx))

    # ----------------------------------------------------------------- ajustes
    def abrir_ajustes(self) -> None:
        from .ventanas.ajustes import VentanaAjustes
        from .nucleo import pantalla as pant

        if self.ventana_ajustes is None:
            self.ventana_ajustes = VentanaAjustes(self)
            area = pant.pantalla_del_mouse().availableGeometry()
            self.ventana_ajustes.move(
                area.center().x() - self.ventana_ajustes.width() // 2,
                area.center().y() - self.ventana_ajustes.height() // 2,
            )
        self.ventana_ajustes.show()
        self.ventana_ajustes.raise_()
        self.ventana_ajustes.activateWindow()

    def aplicar_atajo(self) -> bool:
        """(Re)registra el atajo global. False si la combinacion esta ocupada."""
        return self.atajo.aplicar(self.config.atajo)

    # -------------------------------------------------------------------- salir
    def salir(self) -> None:
        self.atajo.quitar()
        self.bandeja.hide()
        self.qapp.quit()

    def correr(self) -> int:
        return self.qapp.exec()


def _ya_esta_abierta() -> QSharedMemory | None:
    """
    Evita que queden dos iconos en la bandeja.

    Reserva un pedacito de memoria con un nombre fijo: si ya estaba reservado,
    significa que otra copia de la app esta corriendo. Hay que conservar el
    objeto devuelto mientras la app vive, por eso se retorna.
    """
    memoria = QSharedMemory(f"{APP_NOMBRE}-instancia-unica")
    if memoria.attach():
        memoria.detach()
        return None
    return memoria if memoria.create(1) else None


def main() -> int:
    testigo = _ya_esta_abierta()
    if testigo is None:
        # Ya hay una copia andando: no hace falta avisar nada.
        return 0
    app = Aplicacion(sys.argv)
    app.testigo = testigo
    return app.correr()


if __name__ == "__main__":
    raise SystemExit(main())
