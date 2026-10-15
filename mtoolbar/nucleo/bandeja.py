# -*- coding: utf-8 -*-
"""
ICONO DE LA BANDEJA DEL SISTEMA (al lado del reloj).

Click izquierdo: abre la barra flotante.
Click derecho: menu con las herramientas, sus acciones extra, Ajustes y Salir.
"""

from __future__ import annotations

from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from .. import APP_NOMBRE, APP_VERSION
from .herramienta import herramientas_ordenadas
from .iconos import icono, icono_app


class Bandeja(QSystemTrayIcon):
    def __init__(self, app) -> None:  # noqa: ANN001
        super().__init__(icono_app(), app.qapp)
        self._app = app
        self.setToolTip(f"{APP_NOMBRE} {APP_VERSION}")
        self.setContextMenu(self._construir_menu())
        self.activated.connect(self._al_hacer_click)

    def _construir_menu(self) -> QMenu:
        menu = QMenu()
        menu.addAction("Abrir barra", self._app.mostrar_barra)
        menu.addSeparator()

        # Una entrada por herramienta, con sus acciones extra como submenu.
        for herramienta in herramientas_ordenadas():
            extras = herramienta.acciones_extra(self._app.ctx)
            if extras:
                sub = menu.addMenu(icono(herramienta.icono), herramienta.nombre)
                sub.addAction(
                    herramienta.nombre,
                    lambda h=herramienta: self._app.ejecutar_herramienta(h),
                )
                sub.addSeparator()
                for etiqueta, funcion in extras:
                    sub.addAction(etiqueta, lambda f=funcion: f())
            else:
                menu.addAction(
                    icono(herramienta.icono), herramienta.nombre,
                    lambda h=herramienta: self._app.ejecutar_herramienta(h),
                )

        menu.addSeparator()
        menu.addAction(icono("ajustes.svg"), "Ajustes...", self._app.abrir_ajustes)
        menu.addAction("Salir", self._app.salir)
        return menu

    def _al_hacer_click(self, razon) -> None:  # noqa: ANN001
        if razon in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self._app.alternar_barra()
