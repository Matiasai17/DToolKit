# -*- coding: utf-8 -*-
"""
HERRAMIENTA 3: Traductor (espanol <-> ingles, y chino hacia los dos).

Uso rapido: copia un texto en cualquier lado (Ctrl+C), abri la barra y
apreta 3. La ventana aparece con el texto ya traducido.

Usa Google Translate (sin clave) o DeepL (si cargaste una clave gratuita en
Ajustes). La logica de traduccion esta en nucleo/traduccion.py.
"""

from __future__ import annotations

from ..nucleo.herramienta import Herramienta, registrar
from ..ventanas.traductor import VentanaTraductor


@registrar
class Traductor(Herramienta):
    id = "traductor"
    nombre = "Traducir lo copiado"
    icono = "traducir.svg"
    atajo_local = "3"
    orden = 30

    def ejecutar(self, ctx) -> None:  # noqa: ANN001
        VentanaTraductor.abrir(ctx, ctx.leer_texto())

    def acciones_extra(self, ctx) -> list:  # noqa: ANN001
        return [("Abrir el traductor vacio", lambda: VentanaTraductor.abrir(ctx))]
