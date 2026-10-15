# -*- coding: utf-8 -*-
"""
EL CONTRATO DE LAS HERRAMIENTAS.

Cada herramienta es una clase que hereda de `Herramienta` y se anota con el
decorador `@registrar`. La barra flotante lee el REGISTRO y dibuja un boton por
cada herramienta registrada: no hay que tocar la barra para sumar una nueva.

Ejemplo minimo (archivo mtoolbar/herramientas/saludo.py):

    from ..nucleo.herramienta import Herramienta, registrar

    @registrar
    class Saludo(Herramienta):
        id = "saludo"
        nombre = "Decir hola"
        icono = "saludo.svg"
        orden = 50

        def ejecutar(self, ctx):
            ctx.avisar("Hola!")
"""

from __future__ import annotations


class Herramienta:
    """Clase base de la que hereda cada herramienta."""

    # Identificador interno, sin espacios. Se usa para guardar preferencias.
    id: str = ""
    # Nombre visible: aparece en el tooltip del boton y en el menu de la bandeja.
    nombre: str = ""
    # Archivo SVG dentro de mtoolbar/recursos/iconos/
    icono: str = ""
    # Tecla que activa la herramienta mientras la barra esta abierta ("1", "2", "c"...).
    # Dejalo vacio si no queres atajo.
    atajo_local: str = ""
    # Posicion en la barra: menor numero = mas a la izquierda.
    orden: int = 100
    # Si es True, la barra se cierra antes de ejecutar la herramienta
    # (necesario para cualquier cosa que capture la pantalla).
    cerrar_barra_antes: bool = True

    def ejecutar(self, ctx) -> None:          # noqa: ANN001
        """Lo que hace la herramienta. Lo unico obligatorio de implementar."""
        raise NotImplementedError

    # Opcional: acciones extra que aparecen al hacer click derecho en el boton
    # y en el menu de la bandeja. Devolve una lista de (etiqueta, funcion).
    def acciones_extra(self, ctx) -> list:    # noqa: ANN001
        return []


# Lista de clases registradas, en el orden en que se importaron.
REGISTRO: list[type[Herramienta]] = []


def registrar(cls: type[Herramienta]) -> type[Herramienta]:
    """Decorador que agrega la herramienta al registro."""
    if not cls.id:
        raise ValueError(f"La herramienta {cls.__name__} no tiene 'id'")
    REGISTRO.append(cls)
    return cls


def herramientas_ordenadas() -> list[Herramienta]:
    """Devuelve una instancia de cada herramienta, ordenada por 'orden'."""
    return [cls() for cls in sorted(REGISTRO, key=lambda c: (c.orden, c.nombre))]
