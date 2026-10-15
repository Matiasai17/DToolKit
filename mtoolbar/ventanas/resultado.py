# -*- coding: utf-8 -*-
"""
Ventanita con el contenido decodificado de un codigo.

Muestra el formato detectado y el texto, con botones "Copiar" y "Abrir"
(este ultimo solo si el contenido es un enlace).
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget,
)

from .. import tema

# Se guarda la referencia para que Python no destruya la ventana.
_abiertas: list["VentanaResultado"] = []


def _es_enlace(texto: str) -> bool:
    return texto.strip().lower().startswith(("http://", "https://"))


def _etiqueta_contenido(texto: str) -> str:
    """Un titulo descriptivo segun el tipo de contenido del codigo."""
    t = texto.strip()
    if _es_enlace(t):
        return "Enlace"
    if t.lower().startswith("mailto:"):
        return "Correo electronico"
    if t.upper().startswith("WIFI:"):
        return "Red Wi-Fi"
    if t.upper().startswith("BEGIN:VCARD"):
        return "Contacto"
    if t.isdigit():
        return "Numero"
    return "Texto"


class VentanaResultado(QWidget):
    """Ventana sin bordes, con el mismo lenguaje visual que la barra."""

    def __init__(self, ctx, resultados: list) -> None:  # noqa: ANN001
        super().__init__(None)
        self._ctx = ctx
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        # El panel interno es el que lleva el fondo y el borde redondeado (QSS).
        panel = QWidget(self)
        panel.setObjectName("panel")
        contenedor = QVBoxLayout(self)
        contenedor.setContentsMargins(0, 0, 0, 0)
        contenedor.addWidget(panel)

        caja = QVBoxLayout(panel)
        caja.setContentsMargins(
            tema.PADDING_VENTANA, tema.PADDING_VENTANA,
            tema.PADDING_VENTANA, tema.PADDING_VENTANA,
        )
        caja.setSpacing(10)

        from ..herramientas.codigos import nombre_formato

        principal = resultados[0]
        self._texto = principal.text or ""

        titulo = QLabel(_etiqueta_contenido(self._texto), panel)
        titulo.setObjectName("titulo")
        caja.addWidget(titulo)

        detalle = nombre_formato(principal)
        if len(resultados) > 1:
            detalle += f"   -   se encontraron {len(resultados)} codigos"
        sub = QLabel(detalle, panel)
        sub.setObjectName("suave")
        caja.addWidget(sub)

        self._visor = QPlainTextEdit(panel)
        self._visor.setPlainText(self._todo(resultados, nombre_formato))
        self._visor.setReadOnly(True)
        self._visor.setMinimumWidth(420)
        self._visor.setMaximumHeight(170)
        caja.addWidget(self._visor)

        botones = QHBoxLayout()
        botones.setSpacing(8)
        botones.addStretch(1)
        if _es_enlace(self._texto):
            abrir = QPushButton("Abrir", panel)
            abrir.setObjectName("principal")
            abrir.clicked.connect(self._abrir)
            botones.addWidget(abrir)
        copiar = QPushButton("Copiar", panel)
        copiar.setObjectName("" if _es_enlace(self._texto) else "principal")
        copiar.clicked.connect(self._copiar)
        botones.addWidget(copiar)
        cerrar = QPushButton("Cerrar", panel)
        cerrar.clicked.connect(self.close)
        botones.addWidget(cerrar)
        caja.addLayout(botones)

        QShortcut(QKeySequence(Qt.Key_Escape), self).activated.connect(self.close)
        QShortcut(QKeySequence("Ctrl+C"), self).activated.connect(self._copiar)

        self.adjustSize()

    # ------------------------------------------------------------------- ayudas
    @staticmethod
    def _todo(resultados: list, nombre_formato) -> str:  # noqa: ANN001
        if len(resultados) == 1:
            return resultados[0].text or ""
        partes = []
        for i, r in enumerate(resultados, 1):
            partes.append(f"[{i}] {nombre_formato(r)}\n{r.text or ''}")
        return "\n\n".join(partes)

    def _copiar(self) -> None:
        self._ctx.copiar_texto(self._visor.toPlainText())
        self._ctx.avisar("Copiado")

    def _abrir(self) -> None:
        self._ctx.abrir_url(self._texto.strip())
        self.close()

    def closeEvent(self, evento) -> None:  # noqa: N802, ANN001
        if self in _abiertas:
            _abiertas.remove(self)
        super().closeEvent(evento)

    # ------------------------------------------------------------------- publico
    @classmethod
    def abrir(cls, ctx, resultados: list) -> "VentanaResultado":  # noqa: ANN001
        from ..nucleo import pantalla as pant

        ventana = cls(ctx, resultados)
        area = pant.pantalla_del_mouse().availableGeometry()
        ventana.move(
            area.center().x() - ventana.width() // 2,
            area.center().y() - ventana.height() // 2,
        )
        _abiertas.append(ventana)
        ventana.show()
        ventana.raise_()
        ventana.activateWindow()
        return ventana
