# -*- coding: utf-8 -*-
"""
HERRAMIENTA 1: Captura de pantalla.

Oscurece la pantalla, deja seleccionar un area, copia el resultado al
portapapeles y (si la preferencia esta activada) lo guarda como PNG.
"""

from __future__ import annotations

from ..nucleo.herramienta import Herramienta, registrar


@registrar
class Captura(Herramienta):
    id = "captura"
    nombre = "Captura de pantalla"
    icono = "captura.svg"
    atajo_local = "1"
    orden = 10

    def ejecutar(self, ctx) -> None:  # noqa: ANN001
        # Esc o click derecho devuelven None: el usuario cancelo.
        imagen = ctx.seleccionar_area()
        if imagen is None:
            return
        self._procesar(ctx, imagen)

    def acciones_extra(self, ctx) -> list:  # noqa: ANN001
        return [
            ("Capturar el monitor completo", lambda: self._completa(ctx)),
            ("Abrir la carpeta de capturas", lambda: self._abrir_carpeta(ctx)),
        ]

    # ------------------------------------------------------------------ interno
    def _procesar(self, ctx, imagen) -> None:  # noqa: ANN001
        ctx.copiar_imagen(imagen)
        if not ctx.config.guardar_automatico:
            ctx.avisar("Copiado")
            return
        ruta = ctx.guardar_png(imagen, "Captura")
        ctx.avisar("Copiado y guardado" if ruta else "Copiado (no se pudo guardar)")

    def _completa(self, ctx) -> None:  # noqa: ANN001
        imagen = ctx.capturar_pantalla_completa()
        if imagen is not None:
            self._procesar(ctx, imagen)

    def _abrir_carpeta(self, ctx) -> None:  # noqa: ANN001
        ctx.abrir_carpeta(ctx.config.asegurar_carpeta())
