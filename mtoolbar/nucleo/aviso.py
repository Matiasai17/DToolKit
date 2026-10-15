# -*- coding: utf-8 -*-
"""
Aviso flotante chico tipo "Copiado".

Aparece cerca del borde inferior del monitor donde esta el mouse, con un
fundido suave, y se va solo. No usa las notificaciones de Windows para no
dejar ruido en el centro de notificaciones.
"""

from __future__ import annotations

from PySide6.QtCore import QPropertyAnimation, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QLabel, QWidget

from .. import tema
from . import pantalla as pant

# Avisos visibles ahora mismo: se apilan hacia arriba.
_abiertos: list["_Aviso"] = []


class _Aviso(QWidget):
    def __init__(self, texto: str) -> None:
        super().__init__(None)
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
            | Qt.WindowTransparentForInput | Qt.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        self._etiqueta = QLabel(texto, self)
        self._etiqueta.setFont(QFont(tema.FUENTE, tema.TAMANO_TEXTO))
        self._etiqueta.setStyleSheet(
            f"color: {tema.COLOR_TEXTO_AVISO}; background: transparent;"
        )
        self._etiqueta.move(tema.PADDING_AVISO_H, tema.PADDING_AVISO_V)
        self._etiqueta.adjustSize()
        self.resize(
            self._etiqueta.width() + 2 * tema.PADDING_AVISO_H,
            self._etiqueta.height() + 2 * tema.PADDING_AVISO_V,
        )
        self._ubicar()
        self.setWindowOpacity(0.0)

    def _ubicar(self) -> None:
        area = pant.pantalla_del_mouse().availableGeometry()
        x = area.center().x() - self.width() // 2
        y = area.bottom() - self.height() - 90 - 46 * len(_abiertos)
        self.move(x, y)

    def paintEvent(self, evento) -> None:  # noqa: N802, ANN001
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(tema.COLOR_FONDO_AVISO))
        p.drawRoundedRect(self.rect(), tema.RADIO_AVISO, tema.RADIO_AVISO)
        p.end()

    def mostrar(self) -> None:
        _abiertos.append(self)
        self.show()
        self._entrada = QPropertyAnimation(self, b"windowOpacity", self)
        self._entrada.setDuration(tema.DURACION_FUNDIDO_MS)
        self._entrada.setEndValue(1.0)
        self._entrada.start()
        QTimer.singleShot(tema.DURACION_AVISO_MS, self._irse)

    def _irse(self) -> None:
        self._salida = QPropertyAnimation(self, b"windowOpacity", self)
        self._salida.setDuration(tema.DURACION_FUNDIDO_MS)
        self._salida.setEndValue(0.0)
        self._salida.finished.connect(self._fin)
        self._salida.start()

    def _fin(self) -> None:
        if self in _abiertos:
            _abiertos.remove(self)
        self.close()


def avisar(texto: str) -> None:
    """Muestra el aviso. Se puede llamar desde cualquier parte de la app."""
    _Aviso(texto).mostrar()
