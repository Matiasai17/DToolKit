# -*- coding: utf-8 -*-
"""
Punto de entrada para doble click / inicio de Windows.
Equivale a ejecutar:  python -m mtoolbar

Tambien acepta:
    ejecutar.py --autoprueba [archivo.txt]
que comprueba que todo funcione y sale, sin abrir la app. Se usa sobre todo
para verificar el .exe empaquetado.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def _principal() -> int:
    if "--autoprueba" in sys.argv:
        from mtoolbar.autoprueba import correr

        sueltos = [a for a in sys.argv[1:] if not a.startswith("-")]
        if sueltos:
            destino = Path(sueltos[0])
        elif getattr(sys, "frozen", False):
            # Desde el .exe no hay consola: el resultado va a un archivo al lado.
            destino = Path(sys.executable).with_name("autoprueba.txt")
        else:
            destino = None
        return correr(destino)

    from mtoolbar.__main__ import main

    return main()


if __name__ == "__main__":
    raise SystemExit(_principal())
