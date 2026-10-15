# -*- coding: utf-8 -*-
"""
Captura de pantalla: congelar los monitores y recortar una region.

Trabaja con dos sistemas de coordenadas:
  - "logicas": las que usa Qt para ubicar ventanas (afectadas por el escalado
    de Windows, 125%, 150%, etc.).
  - "fisicas": los pixeles reales del monitor, que es lo que queremos guardar.
La relacion entre ambas es el devicePixelRatio (dpr) de cada monitor.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QGuiApplication, QImage, QPainter, QPixmap, QScreen


@dataclass
class PantallaCongelada:
    """Una foto de un monitor, mas los datos para pasar de logico a fisico."""

    pantalla: QScreen
    geometria: QRect           # geometria logica del monitor
    imagen: QPixmap            # foto en pixeles fisicos
    dpr: float = 1.0


@dataclass
class Congelado:
    """El escritorio completo congelado en el instante en que se abrio el overlay."""

    pantallas: list[PantallaCongelada] = field(default_factory=list)

    def recortar(self, rect_logico: QRect) -> QPixmap | None:
        """Recorta la region indicada (en coordenadas logicas globales)."""
        rect_logico = rect_logico.normalized()
        if rect_logico.width() < 1 or rect_logico.height() < 1:
            return None

        partes = [p for p in self.pantallas if p.geometria.intersects(rect_logico)]
        if not partes:
            return None

        # Caso habitual: la seleccion esta dentro de un solo monitor.
        if len(partes) == 1:
            p = partes[0]
            local = rect_logico.translated(-p.geometria.topLeft())
            fisico = QRect(
                round(local.x() * p.dpr), round(local.y() * p.dpr),
                round(local.width() * p.dpr), round(local.height() * p.dpr),
            ).intersected(QRect(0, 0, p.imagen.width(), p.imagen.height()))
            recorte = p.imagen.copy(fisico)
            recorte.setDevicePixelRatio(p.dpr)
            return recorte

        # Seleccion a caballo entre varios monitores: se compone en el dpr mayor.
        dpr = max(p.dpr for p in partes)
        destino = QImage(
            round(rect_logico.width() * dpr), round(rect_logico.height() * dpr),
            QImage.Format_ARGB32,
        )
        destino.fill(Qt.black)
        pintor = QPainter(destino)
        pintor.setRenderHint(QPainter.SmoothPixmapTransform, True)
        for p in partes:
            comun = p.geometria.intersected(rect_logico)
            origen_local = comun.translated(-p.geometria.topLeft())
            origen = QRect(
                round(origen_local.x() * p.dpr), round(origen_local.y() * p.dpr),
                round(origen_local.width() * p.dpr), round(origen_local.height() * p.dpr),
            )
            destino_local = comun.translated(-rect_logico.topLeft())
            cajon = QRect(
                round(destino_local.x() * dpr), round(destino_local.y() * dpr),
                round(destino_local.width() * dpr), round(destino_local.height() * dpr),
            )
            pintor.drawPixmap(cajon, p.imagen, origen)
        pintor.end()
        recorte = QPixmap.fromImage(destino)
        recorte.setDevicePixelRatio(dpr)
        return recorte

    def pantalla_en(self, punto: QPoint) -> PantallaCongelada | None:
        for p in self.pantallas:
            if p.geometria.contains(punto):
                return p
        return self.pantallas[0] if self.pantallas else None


def congelar() -> Congelado:
    """Saca una foto de todos los monitores en este instante."""
    congelado = Congelado()
    for pantalla in QGuiApplication.screens():
        geo = pantalla.geometry()
        # grabWindow(0) sobre un QScreen captura ese monitor completo.
        foto = pantalla.grabWindow(0)
        dpr = foto.width() / geo.width() if geo.width() else pantalla.devicePixelRatio()
        foto.setDevicePixelRatio(dpr)
        congelado.pantallas.append(PantallaCongelada(pantalla, geo, foto, dpr))
    return congelado


def geometria_virtual() -> QRect:
    """El rectangulo que engloba todos los monitores (coordenadas logicas)."""
    total = QRect()
    for pantalla in QGuiApplication.screens():
        total = total.united(pantalla.geometry())
    return total


def pantalla_del_mouse() -> QScreen:
    """El monitor donde esta el puntero del mouse ahora mismo."""
    pos = QGuiApplication.primaryScreen().availableGeometry().center()
    try:
        from PySide6.QtGui import QCursor
        pos = QCursor.pos()
    except Exception:
        pass
    return QGuiApplication.screenAt(pos) or QGuiApplication.primaryScreen()
