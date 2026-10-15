# -*- coding: utf-8 -*-
"""
AUTOPRUEBA: comprueba que la app (o el .exe empaquetado) funciona.

Sirve sobre todo despues de tocar build.bat o MToolBar.spec: el empaquetado
recorta librerias que no se usan, y esto confirma que no se recorto de mas.

Se corre asi:

    MToolBar.exe --autoprueba            (deja el resultado en autoprueba.txt)
    .venv\\Scripts\\python ejecutar.py --autoprueba

Sale con codigo 0 si todo paso, 1 si algo fallo.
"""

from __future__ import annotations

import sys
from pathlib import Path


class _Aviso(Exception):
    """Algo que no depende de la app (por ejemplo, no hay internet): no cuenta como falla."""


def correr(destino: Path | None = None) -> int:
    lineas: list[str] = []
    fallos = 0

    def revisar(nombre: str, funcion) -> None:  # noqa: ANN001
        nonlocal fallos
        try:
            detalle = funcion()
            lineas.append(f"[OK]    {nombre}: {detalle}")
        except _Aviso as aviso:
            lineas.append(f"[AVISO] {nombre}: {aviso}")
        except Exception as error:  # noqa: BLE001
            fallos += 1
            lineas.append(f"[FALLA] {nombre}: {type(error).__name__}: {error}")

    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv[:1])

    # 1) Qt arranco de verdad (si faltara el plugin de plataforma, ni llegamos aca)
    def _qt() -> str:
        from PySide6 import __version__
        from PySide6.QtGui import QGuiApplication
        plat = QGuiApplication.platformName()
        pantallas = len(QGuiApplication.screens())
        return f"PySide6 {__version__}, plataforma '{plat}', {pantallas} monitor(es)"
    revisar("Qt", _qt)

    # 2) Los iconos SVG se cargan y se recolorean
    def _iconos() -> str:
        from .nucleo.iconos import icono, icono_app
        px = icono("captura.svg").pixmap(20, 20)
        if px.isNull() or px.width() == 0:
            raise RuntimeError("el icono salio vacio (falta el plugin de SVG?)")
        if icono_app().isNull():
            raise RuntimeError("el icono de la bandeja salio vacio")
        return f"captura.svg -> {px.width()}x{px.height()} px"
    revisar("Iconos SVG", _iconos)

    # 3) La barra se arma con sus herramientas
    def _barra() -> str:
        from .config import Config
        from .nucleo.barra import Barra
        from .nucleo.contexto import Contexto
        from .nucleo.herramienta import REGISTRO
        from . import herramientas  # noqa: F401

        class _App:
            def ocultar_barra(self) -> None: ...
            def abrir_ajustes(self) -> None: ...

        barra = Barra(Contexto(Config(), _App()))
        barra.adjustSize()
        if not REGISTRO:
            raise RuntimeError("no se registro ninguna herramienta")
        return (f"{len(REGISTRO)} herramientas, barra de "
                f"{barra.width()}x{barra.height()} px")
    revisar("Barra de herramientas", _barra)

    # 4) Decodificar QR, EAN-13 y Code 128
    def _codigos() -> str:
        import zxingcpp
        from PySide6.QtGui import QImage
        from .herramientas.codigos import _decodificar

        casos = [("QRCode", "https://example.com"), ("EAN13", "7790895000126"),
                 ("Code128", "LOTE-2026-A")]
        leidos = []
        for formato, dato in casos:
            svg = zxingcpp.create_barcode(
                dato, zxingcpp.barcode_format_from_str(formato)).to_svg(scale=5)
            img = QImage()
            img.loadFromData(svg.encode("utf8"), "SVG")
            res = _decodificar(img)
            if not res or res[0].text != dato:
                raise RuntimeError(f"no se pudo leer un {formato}")
            leidos.append(formato)
        return ", ".join(leidos)
    revisar("Lector de codigos", _codigos)

    # 5) Capturar la pantalla
    def _captura() -> str:
        from PySide6.QtCore import QRect
        from .nucleo import pantalla as pant

        congelado = pant.congelar()
        if not congelado.pantallas:
            raise RuntimeError("no se detecto ningun monitor")
        recorte = congelado.recortar(
            QRect(congelado.pantallas[0].geometria.topLeft(), QRect(0, 0, 120, 80).size())
        )
        if recorte is None or recorte.isNull():
            raise RuntimeError("el recorte salio vacio")
        return f"recorte de {recorte.width()}x{recorte.height()} px"
    revisar("Captura de pantalla", _captura)

    # 6) Portapapeles
    def _portapapeles() -> str:
        from PySide6.QtGui import QGuiApplication
        anterior = QGuiApplication.clipboard().text()
        QGuiApplication.clipboard().setText("MToolBar autoprueba")
        leido = QGuiApplication.clipboard().text()
        QGuiApplication.clipboard().setText(anterior)
        if leido != "MToolBar autoprueba":
            raise RuntimeError("no se pudo escribir en el portapapeles")
        return "escribe y lee"
    revisar("Portapapeles", _portapapeles)

    # 7) El atajo global se puede registrar
    def _atajo() -> str:
        from .nucleo.atajo import AtajoGlobal
        a = AtajoGlobal(lambda: None)
        ok = a.aplicar("Ctrl+Alt+F9")
        a.quitar()
        if not ok:
            raise RuntimeError("Windows rechazo el registro del atajo")
        return "Ctrl+Alt+F9 registrado y liberado"
    revisar("Atajo global", _atajo)

    # 8) Traductor sin internet: lectura de respuestas y eleccion de idioma
    def _traductor_local() -> str:
        from .nucleo import traduccion as t

        if t._leer_google([[["Hello ", "Hola ", None], ["world", "mundo", None]],
                           None, "es"]) != ("Hello world", "es"):
            raise RuntimeError("no se entiende la respuesta de Google")
        if t._leer_deepl({"translations": [{"detected_source_language": "EN",
                                            "text": "Hola"}]}) != ("Hola", "en"):
            raise RuntimeError("no se entiende la respuesta de DeepL")
        casos = {"Necesito mandar la factura": "en", "I need to send the invoice": "es",
                 "你好，今天天气很好": t.IDIOMA_DESDE_CHINO}
        for texto, esperado in casos.items():
            if t.adivinar_destino(texto) != esperado:
                raise RuntimeError(f"destino equivocado para {texto!r}")
        return "respuestas de Google y DeepL, es->en, en->es, zh->" + t.IDIOMA_DESDE_CHINO
    revisar("Traductor (local)", _traductor_local)

    # 9) Traductor de verdad: un pedido HTTPS a Google. Si falta el modulo ssl
    # (el empaquetado lo recorto) es FALLA; si no hay internet, solo AVISO.
    def _traductor_red() -> str:
        import ssl  # noqa: F401  (si esto falla, el .exe no puede usar HTTPS)
        from .nucleo import traduccion as t

        try:
            r = t.traducir("Hola, buenos dias", destino="en")
        except t.ErrorTraduccion as error:
            raise _Aviso(f"no se pudo probar en vivo ({error})") from error
        if not r.texto or r.texto.strip().lower().startswith("hola"):
            raise RuntimeError(f"la respuesta no parece una traduccion: {r.texto!r}")
        return f"'Hola, buenos dias' -> {r.texto!r} ({r.motor})"
    revisar("Traductor (internet)", _traductor_red)

    # 10) La bandeja del sistema esta disponible
    def _bandeja() -> str:
        from PySide6.QtWidgets import QSystemTrayIcon
        if not QSystemTrayIcon.isSystemTrayAvailable():
            raise RuntimeError("Windows no expone la bandeja del sistema")
        return "disponible"
    revisar("Bandeja del sistema", _bandeja)

    app.quit()

    resumen = "TODO OK" if fallos == 0 else f"{fallos} PRUEBA(S) FALLARON"
    texto = "\n".join(["Autoprueba de MToolBar", "=" * 46, *lineas, "=" * 46, resumen])
    try:
        print(texto)
    except UnicodeEncodeError:   # consola de Windows sin UTF-8
        print(texto.encode("ascii", "replace").decode("ascii"))
    if destino is not None:
        destino.write_text(texto, encoding="utf-8")
    return 1 if fallos else 0
