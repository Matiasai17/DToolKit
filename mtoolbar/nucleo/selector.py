# -*- coding: utf-8 -*-
"""
Overlay para seleccionar un area de la pantalla.

Funciona como la barra de recortes de Windows: congela la imagen de todos los
monitores, la muestra oscurecida y deja arrastrar un rectangulo.

  - Arrastrar con el boton izquierdo  -> selecciona ese area
  - Enter / doble click               -> el monitor completo
  - Esc / boton derecho               -> cancelar

Se usa siempre a traves del contexto:  pix = ctx.seleccionar_area()
"""

from __future__ import annotations

from PySide6.QtCore import QEventLoop, QPoint, QRect, Qt
from PySide6.QtGui import QColor, QCursor, QFont, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QWidget

from .. import tema
from . import pantalla as pant


class _Capa(QWidget):
    """Una ventana sin bordes que cubre un monitor y dibuja la seleccion."""

    def __init__(self, foto: pant.PantallaCongelada, dueno: "Selector") -> None:
        super().__init__(None)
        self._foto = foto
        self._dueno = dueno
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
            | Qt.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setCursor(Qt.CrossCursor)
        self.setMouseTracking(True)
        self.setGeometry(foto.geometria)

    # -- dibujo ------------------------------------------------------------
    def paintEvent(self, evento) -> None:  # noqa: N802, ANN001
        p = QPainter(self)
        origen = self._foto.geometria.topLeft()

        # 1) la foto congelada del monitor
        p.drawPixmap(self.rect(), self._foto.imagen)
        # 2) el velo oscuro encima
        p.fillRect(self.rect(), QColor(tema.COLOR_OSCURECER))

        sel = self._dueno.seleccion_global()
        if not sel.isValid() or sel.isNull():
            self._dibujar_guias(p)
            p.end()
            return

        local = sel.translated(-origen)
        # 3) el area elegida se vuelve a dibujar sin velo
        dpr = self._foto.dpr
        p.drawPixmap(
            local,
            self._foto.imagen,
            QRect(round(local.x() * dpr), round(local.y() * dpr),
                  round(local.width() * dpr), round(local.height() * dpr)),
        )
        # 4) borde de acento
        lapiz = QPen(QColor(tema.COLOR_ACENTO), tema.GROSOR_SELECCION)
        lapiz.setJoinStyle(Qt.MiterJoin)
        p.setPen(lapiz)
        p.setBrush(Qt.NoBrush)
        p.drawRect(local.adjusted(0, 0, -1, -1))
        # 5) cartelito con las medidas
        if tema.MOSTRAR_MEDIDAS:
            self._dibujar_medidas(p, local, sel)
        p.end()

    def _dibujar_guias(self, p: QPainter) -> None:
        """La cruz que sigue al mouse antes de empezar a arrastrar."""
        if not tema.MOSTRAR_GUIAS:
            return
        pos = self.mapFromGlobal(QCursor.pos())
        if not self.rect().contains(pos):
            return
        p.setPen(QPen(QColor(tema.COLOR_GUIAS), tema.GROSOR_GUIAS))
        p.drawLine(0, pos.y(), self.width(), pos.y())
        p.drawLine(pos.x(), 0, pos.x(), self.height())

    def _dibujar_medidas(self, p: QPainter, local: QRect, sel: QRect) -> None:
        texto = f"{sel.width()} x {sel.height()}"
        p.setFont(QFont(tema.FUENTE, tema.TAMANO_TEXTO_CHICO))
        ancho = p.fontMetrics().horizontalAdvance(texto) + 2 * tema.PADDING_AVISO_H
        alto = p.fontMetrics().height() + tema.PADDING_AVISO_V
        y = local.y() - alto - 6
        if y < 0:                      # si no entra arriba, va adentro
            y = local.y() + 6
        caja = QRect(local.x(), y, ancho, alto)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(tema.COLOR_FONDO_AVISO))
        p.drawRoundedRect(caja, tema.RADIO_AVISO, tema.RADIO_AVISO)
        p.setPen(QColor(tema.COLOR_TEXTO_AVISO))
        p.drawText(caja, Qt.AlignCenter, texto)

    # -- mouse y teclado ---------------------------------------------------
    def mousePressEvent(self, e) -> None:  # noqa: N802, ANN001
        if e.button() == Qt.RightButton:
            self._dueno.cancelar()
            return
        if e.button() == Qt.LeftButton:
            # grabMouse permite seguir arrastrando aunque el puntero pase a
            # otro monitor: los eventos siguen llegando a esta capa.
            self.grabMouse()
            self._dueno.empezar(e.globalPosition().toPoint())

    def mouseMoveEvent(self, e) -> None:  # noqa: N802, ANN001
        self._dueno.mover(e.globalPosition().toPoint())

    def mouseReleaseEvent(self, e) -> None:  # noqa: N802, ANN001
        if e.button() == Qt.LeftButton:
            self.releaseMouse()
            self._dueno.terminar(e.globalPosition().toPoint())

    def mouseDoubleClickEvent(self, e) -> None:  # noqa: N802, ANN001
        self._dueno.tomar_monitor_completo(e.globalPosition().toPoint())

    def keyPressEvent(self, e) -> None:  # noqa: N802, ANN001
        if e.key() == Qt.Key_Escape:
            self._dueno.cancelar()
        elif e.key() in (Qt.Key_Return, Qt.Key_Enter):
            self._dueno.tomar_monitor_completo(QCursor.pos())


class Selector:
    """Coordina las capas de todos los monitores y devuelve el recorte."""

    def __init__(self) -> None:
        self._congelado = pant.congelar()
        self._capas: list[_Capa] = []
        self._inicio: QPoint | None = None
        self._actual: QPoint | None = None
        self._resultado: QPixmap | None = None
        self._terminado = False
        self._bucle: QEventLoop | None = None

    # -- API ---------------------------------------------------------------
    def pedir_area(self) -> QPixmap | None:
        """Muestra el overlay y no vuelve hasta que el usuario elige o cancela."""
        for foto in self._congelado.pantallas:
            capa = _Capa(foto, self)
            capa.show()
            self._capas.append(capa)
        if self._capas:
            principal = self._capas[0]
            principal.activateWindow()
            principal.raise_()
            principal.setFocus()
        else:
            return None

        # Bucle propio: la herramienta queda esperando el resultado.
        self._bucle = QEventLoop()
        self._bucle.exec()
        return self._resultado

    def seleccion_global(self) -> QRect:
        """El rectangulo elegido hasta ahora, en coordenadas globales."""
        if self._inicio is None or self._actual is None:
            return QRect()
        return QRect(self._inicio, self._actual).normalized()

    # -- eventos que mandan las capas --------------------------------------
    def empezar(self, punto: QPoint) -> None:
        self._inicio = punto
        self._actual = punto
        self._repintar()

    def mover(self, punto: QPoint) -> None:
        self._actual = punto          # si no hay inicio, solo mueve la cruz
        self._repintar()

    def terminar(self, punto: QPoint) -> None:
        if self._inicio is None:
            return
        self._actual = punto
        rect = self.seleccion_global()
        # Un click sin arrastrar no es una seleccion valida: se sigue esperando.
        if rect.width() < 3 or rect.height() < 3:
            self._inicio = None
            self._repintar()
            return
        self._cerrar(self._congelado.recortar(rect))

    def tomar_monitor_completo(self, punto: QPoint) -> None:
        foto = self._congelado.pantalla_en(punto)
        if foto is None:
            self.cancelar()
            return
        self._cerrar(self._congelado.recortar(foto.geometria))

    def cancelar(self) -> None:
        self._cerrar(None)

    # -- interno -----------------------------------------------------------
    def _repintar(self) -> None:
        for capa in self._capas:
            capa.update()

    def _cerrar(self, resultado: QPixmap | None) -> None:
        if self._terminado:
            return
        self._terminado = True
        self._resultado = resultado
        for capa in self._capas:
            capa.releaseMouse()
            capa.close()
        self._capas.clear()
        if self._bucle is not None:
            self._bucle.quit()


def seleccionar_area() -> QPixmap | None:
    """Atajo: abre el overlay y devuelve el recorte (o None si se cancelo)."""
    return Selector().pedir_area()
