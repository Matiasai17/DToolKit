# -*- coding: utf-8 -*-
"""
LA BARRA FLOTANTE.

Ventana chica sin bordes, oscura y semitransparente, centrada arriba del
monitor donde esta el mouse (parecida a la barra de recortes de Windows).

No sabe nada de las herramientas: recorre el REGISTRO y dibuja un boton por
cada una. Agregar una herramienta no requiere tocar este archivo.

Se cierra con Esc o al hacer click afuera (cuando pierde el foco).
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QSize, Qt, QTimer
from PySide6.QtGui import QColor, QKeySequence, QPainter, QPainterPath, QPen, QShortcut
from PySide6.QtWidgets import QFrame, QHBoxLayout, QMenu, QToolButton, QWidget

from .. import tema
from . import pantalla as pant
from .herramienta import Herramienta, herramientas_ordenadas
from .iconos import icono


class BotonHerramienta(QToolButton):
    """Un boton de la barra. Click izquierdo ejecuta; click derecho = extras."""

    def __init__(self, herramienta: Herramienta, barra: "Barra") -> None:
        super().__init__(barra)
        self._herramienta = herramienta
        self._barra = barra
        self.setObjectName("herramienta")
        self.setIcon(icono(herramienta.icono))
        self.setIconSize(QSize(tema.TAMANO_ICONO, tema.TAMANO_ICONO))
        self.setFixedSize(tema.TAMANO_BOTON, tema.TAMANO_BOTON)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)
        pista = herramienta.nombre
        if herramienta.atajo_local:
            pista = f"{pista}  ({herramienta.atajo_local.upper()})"
        self.setToolTip(pista)
        self.clicked.connect(lambda: barra.ejecutar(herramienta))
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._menu_extras)

    def _menu_extras(self) -> None:
        extras = self._herramienta.acciones_extra(self._barra.ctx)
        if not extras:
            return
        menu = QMenu(self)
        for etiqueta, funcion in extras:
            menu.addAction(etiqueta, lambda f=funcion: self._barra.ejecutar_extra(f))
        menu.exec(self.mapToGlobal(self.rect().bottomLeft()))


class Barra(QWidget):
    """La barra flotante con los botones de las herramientas."""

    def __init__(self, ctx) -> None:  # noqa: ANN001
        super().__init__(None)
        self.ctx = ctx
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
            | Qt.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setObjectName("barra")

        self._caja = QHBoxLayout(self)
        self._caja.setContentsMargins(
            tema.PADDING_BARRA, tema.PADDING_BARRA,
            tema.PADDING_BARRA, tema.PADDING_BARRA,
        )
        self._caja.setSpacing(tema.ESPACIO_BOTONES)

        self._herramientas: list[Herramienta] = []
        self._construir()

        # Esc cierra la barra.
        atajo_esc = QShortcut(QKeySequence(Qt.Key_Escape), self)
        atajo_esc.activated.connect(self.hide)

    # ------------------------------------------------------------- construccion
    def _construir(self) -> None:
        """Crea un boton por herramienta registrada, mas los fijos del final."""
        self._herramientas = herramientas_ordenadas()
        for herramienta in self._herramientas:
            self._caja.addWidget(BotonHerramienta(herramienta, self))
            if herramienta.atajo_local:
                atajo = QShortcut(QKeySequence(herramienta.atajo_local), self)
                atajo.activated.connect(lambda h=herramienta: self.ejecutar(h))

        # Separador + boton de ajustes, siempre al final.
        separador = QFrame(self)
        separador.setObjectName("separador")
        separador.setFixedWidth(tema.ANCHO_SEPARADOR)
        separador.setFixedHeight(tema.TAMANO_BOTON - 12)
        self._caja.addWidget(separador)

        boton_ajustes = QToolButton(self)
        boton_ajustes.setObjectName("herramienta")
        boton_ajustes.setIcon(icono("ajustes.svg"))
        boton_ajustes.setIconSize(QSize(tema.TAMANO_ICONO, tema.TAMANO_ICONO))
        boton_ajustes.setFixedSize(tema.TAMANO_BOTON, tema.TAMANO_BOTON)
        boton_ajustes.setCursor(Qt.PointingHandCursor)
        boton_ajustes.setFocusPolicy(Qt.NoFocus)
        boton_ajustes.setToolTip("Ajustes")
        boton_ajustes.clicked.connect(self._abrir_ajustes)
        self._caja.addWidget(boton_ajustes)

        self.adjustSize()

    # ------------------------------------------------------------------- dibujo
    def paintEvent(self, evento) -> None:  # noqa: N802, ANN001
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        borde = tema.GROSOR_BORDE_BARRA
        caja = self.rect().adjusted(0, 0, -1, -1)
        camino = QPainterPath()
        camino.addRoundedRect(caja, tema.RADIO_BARRA, tema.RADIO_BARRA)
        p.fillPath(camino, QColor(tema.COLOR_FONDO_BARRA))
        if borde > 0:
            p.setPen(QPen(QColor(tema.COLOR_BORDE_BARRA), borde))
            p.drawPath(camino)
        p.end()

    # ---------------------------------------------------------------- mostrarse
    def _ubicacion(self, area) -> tuple[int, int]:  # noqa: ANN001
        """
        Calcula donde poner la barra segun tema.POSICION_BARRA.

        `area` es el area util del monitor (ya descuenta la barra de tareas).
        """
        mx, my = tema.MARGEN_PANTALLA_X, tema.MARGEN_PANTALLA_Y
        izq = area.left() + mx
        der = area.right() - self.width() - mx + 1
        centro_x = area.center().x() - self.width() // 2
        arriba = area.top() + my
        abajo = area.bottom() - self.height() - my + 1
        centro_y = area.center().y() - self.height() // 2

        posiciones = {
            "abajo-derecha": (der, abajo),
            "abajo-centro": (centro_x, abajo),
            "abajo-izquierda": (izq, abajo),
            "arriba-derecha": (der, arriba),
            "arriba-centro": (centro_x, arriba),
            "arriba-izquierda": (izq, arriba),
            "centro": (centro_x, centro_y),
        }
        if tema.POSICION_BARRA == "mouse":
            from PySide6.QtGui import QCursor
            p = QCursor.pos()
            x, y = p.x() - self.width() // 2, p.y() - self.height() // 2
        else:
            x, y = posiciones.get(tema.POSICION_BARRA, posiciones["abajo-derecha"])

        # Que nunca quede fuera de la pantalla.
        x = max(area.left() + mx, min(x, der))
        y = max(area.top() + my, min(y, abajo))
        return x, y

    def mostrar(self) -> None:
        """Se ubica en el monitor donde esta el mouse y toma el foco."""
        self.adjustSize()
        area = pant.pantalla_del_mouse().availableGeometry()
        self.move(*self._ubicacion(area))
        self.show()
        self.raise_()
        self.activateWindow()
        self.setFocus()

    def event(self, evento) -> bool:  # noqa: ANN001
        # Al perder el foco (click afuera) la barra se oculta.
        if evento.type() == QEvent.WindowDeactivate and self.isVisible():
            self.hide()
        return super().event(evento)

    # -------------------------------------------------------------- ejecucion
    def ejecutar(self, herramienta: Herramienta) -> None:
        """Cierra la barra (si corresponde) y corre la herramienta."""
        if herramienta.cerrar_barra_antes:
            self.hide()
            # Un ciclo de espera para que la barra ya no este en la pantalla
            # cuando la herramienta capture la imagen.
            QTimer.singleShot(90, lambda: herramienta.ejecutar(self.ctx))
        else:
            herramienta.ejecutar(self.ctx)

    def ejecutar_extra(self, funcion) -> None:  # noqa: ANN001
        self.hide()
        QTimer.singleShot(90, funcion)

    def _abrir_ajustes(self) -> None:
        self.hide()
        QTimer.singleShot(50, self.ctx.abrir_ajustes)
