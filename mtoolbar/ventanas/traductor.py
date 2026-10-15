# -*- coding: utf-8 -*-
"""
Ventana del traductor.

Arriba el texto original (editable), en el medio el idioma destino y abajo la
traduccion. El pedido a internet corre en segundo plano para que la ventana no
se congele mientras espera.
"""

from __future__ import annotations

import threading

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QButtonGroup, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QVBoxLayout,
    QWidget,
)

from .. import tema
from ..nucleo import traduccion

# (codigo, etiqueta) de los botones de idioma destino.
DESTINOS = [("auto", "Auto"), ("es", "Espanol"), ("en", "Ingles"), ("zh", "Chino")]

# Se guarda la referencia para que Python no destruya la ventana abierta.
_abierta: list["VentanaTraductor"] = []


class _Trabajador(QObject):
    """Hace el pedido en otro hilo y avisa el resultado con una senal."""

    listo = Signal(int, object)     # (numero de pedido, Resultado)
    fallo = Signal(int, str)        # (numero de pedido, mensaje)

    def lanzar(self, numero: int, texto: str, clave: str, destino: str) -> None:
        def _correr() -> None:
            try:
                self.listo.emit(numero, traduccion.traducir(texto, clave, destino))
            except traduccion.ErrorTraduccion as error:
                self.fallo.emit(numero, str(error))
            except Exception as error:  # noqa: BLE001
                self.fallo.emit(numero, f"Error inesperado: {error}")

        threading.Thread(target=_correr, daemon=True).start()


class VentanaTraductor(QWidget):
    def __init__(self, ctx) -> None:  # noqa: ANN001
        super().__init__(None)
        self._ctx = ctx
        self._pedido = 0                    # para descartar respuestas viejas
        self._trabajador = _Trabajador()
        self._trabajador.listo.connect(self._al_terminar)
        self._trabajador.fallo.connect(self._al_fallar)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_DeleteOnClose, True)

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

        titulo = QLabel("Traducir", panel)
        titulo.setObjectName("titulo")
        caja.addWidget(titulo)

        # --- texto original ------------------------------------------------
        self._origen = QPlainTextEdit(panel)
        self._origen.setPlaceholderText(
            "Escribi o pega el texto aca (o copialo antes de abrir el traductor)"
        )
        self._origen.setMinimumWidth(460)
        self._origen.setFixedHeight(110)
        caja.addWidget(self._origen)

        # --- idioma destino --------------------------------------------------
        fila_idioma = QHBoxLayout()
        fila_idioma.setSpacing(6)
        etiqueta = QLabel("Traducir a:", panel)
        etiqueta.setObjectName("suave")
        fila_idioma.addWidget(etiqueta)
        self._grupo = QButtonGroup(self)
        self._grupo.setExclusive(True)
        for codigo, nombre in DESTINOS:
            boton = QPushButton(nombre, panel)
            boton.setObjectName("idioma")
            boton.setCheckable(True)
            boton.setCursor(Qt.PointingHandCursor)
            boton.setProperty("codigo", codigo)
            boton.setChecked(codigo == "auto")
            self._grupo.addButton(boton)
            fila_idioma.addWidget(boton)
        fila_idioma.addStretch(1)
        self._grupo.buttonClicked.connect(lambda _b: self.traducir())
        caja.addLayout(fila_idioma)

        # --- traduccion ------------------------------------------------------
        self._resultado = QPlainTextEdit(panel)
        self._resultado.setReadOnly(True)
        self._resultado.setPlaceholderText("La traduccion aparece aca")
        self._resultado.setFixedHeight(130)
        caja.addWidget(self._resultado)

        self._estado = QLabel("", panel)
        self._estado.setObjectName("suave")
        self._estado.setWordWrap(True)
        caja.addWidget(self._estado)

        # --- botones ---------------------------------------------------------
        botones = QHBoxLayout()
        botones.setSpacing(8)
        botones.addStretch(1)
        self._boton_traducir = QPushButton("Traducir", panel)
        self._boton_traducir.setToolTip("Ctrl + Enter")
        self._boton_traducir.clicked.connect(self.traducir)
        botones.addWidget(self._boton_traducir)
        self._boton_copiar = QPushButton("Copiar traduccion", panel)
        self._boton_copiar.setObjectName("principal")
        self._boton_copiar.clicked.connect(self._copiar)
        botones.addWidget(self._boton_copiar)
        cerrar = QPushButton("Cerrar", panel)
        cerrar.clicked.connect(self.close)
        botones.addWidget(cerrar)
        caja.addLayout(botones)

        QShortcut(QKeySequence(Qt.Key_Escape), self).activated.connect(self.close)
        QShortcut(QKeySequence("Ctrl+Return"), self).activated.connect(self.traducir)
        QShortcut(QKeySequence("Ctrl+Enter"), self).activated.connect(self.traducir)

        self.adjustSize()

    # ------------------------------------------------------------------ logica
    def _destino(self) -> str:
        boton = self._grupo.checkedButton()
        return boton.property("codigo") if boton else "auto"

    def traducir(self) -> None:
        texto = self._origen.toPlainText().strip()
        if not texto:
            self._estado.setText("No hay texto para traducir.")
            return
        self._pedido += 1
        self._estado.setText("Traduciendo...")
        self._boton_traducir.setEnabled(False)
        self._trabajador.lanzar(
            self._pedido, texto, self._ctx.config.deepl_clave, self._destino()
        )

    def _al_terminar(self, numero: int, resultado) -> None:  # noqa: ANN001
        if numero != self._pedido:
            return                          # llego tarde: ya se pidio otra cosa
        self._boton_traducir.setEnabled(True)
        self._resultado.setPlainText(resultado.texto)
        estado = resultado.descripcion
        if resultado.nota:
            estado += f"\n{resultado.nota}"
        self._estado.setText(estado)

    def _al_fallar(self, numero: int, mensaje: str) -> None:
        if numero != self._pedido:
            return
        self._boton_traducir.setEnabled(True)
        self._estado.setText(mensaje)

    def _copiar(self) -> None:
        texto = self._resultado.toPlainText()
        if texto:
            self._ctx.copiar_texto(texto)
            self._ctx.avisar("Copiado")

    def closeEvent(self, evento) -> None:  # noqa: N802, ANN001
        self._pedido += 1                   # cualquier respuesta pendiente se ignora
        if self in _abierta:
            _abierta.remove(self)
        super().closeEvent(evento)

    # ------------------------------------------------------------------ publico
    @classmethod
    def abrir(cls, ctx, texto: str = "") -> "VentanaTraductor":  # noqa: ANN001
        """Abre (o reutiliza) la ventana y, si hay texto, lo traduce enseguida."""
        from ..nucleo import pantalla as pant

        if _abierta:
            ventana = _abierta[0]
        else:
            ventana = cls(ctx)
            area = pant.pantalla_del_mouse().availableGeometry()
            ventana.move(
                area.center().x() - ventana.width() // 2,
                area.center().y() - ventana.height() // 2,
            )
            _abierta.append(ventana)
        ventana.show()
        ventana.raise_()
        ventana.activateWindow()
        if texto.strip():
            ventana._origen.setPlainText(texto.strip())
            ventana.traducir()
        else:
            ventana._origen.setFocus()
        return ventana
