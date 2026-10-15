# -*- coding: utf-8 -*-
"""
Ventana de Ajustes: carpeta de guardado, atajo global e inicio con Windows.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (
    QCheckBox, QFileDialog, QHBoxLayout, QKeySequenceEdit, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QWidget,
)

from .. import APP_NOMBRE, APP_VERSION, tema


class VentanaAjustes(QWidget):
    def __init__(self, app) -> None:  # noqa: ANN001
        super().__init__(None)
        self._app = app
        self._config = app.config
        self.setWindowTitle(f"Ajustes de {APP_NOMBRE}")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

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
        caja.setSpacing(12)

        titulo = QLabel(f"Ajustes de {APP_NOMBRE}", panel)
        titulo.setObjectName("titulo")
        caja.addWidget(titulo)

        # --- carpeta de guardado ------------------------------------------
        caja.addWidget(self._etiqueta("Carpeta donde se guardan las capturas", panel))
        fila = QHBoxLayout()
        fila.setSpacing(8)
        self._carpeta = QLineEdit(self._config.carpeta_guardado, panel)
        self._carpeta.setReadOnly(True)
        self._carpeta.setMinimumWidth(360)
        fila.addWidget(self._carpeta, 1)
        elegir = QPushButton("Cambiar...", panel)
        elegir.clicked.connect(self._elegir_carpeta)
        fila.addWidget(elegir)
        caja.addLayout(fila)

        self._guardar = QCheckBox("Guardar la captura como PNG automaticamente", panel)
        self._guardar.setChecked(self._config.guardar_automatico)
        self._guardar.toggled.connect(self._cambio_guardado)
        caja.addWidget(self._guardar)

        # --- atajo global --------------------------------------------------
        caja.addWidget(self._etiqueta("Atajo para abrir la barra", panel))
        fila2 = QHBoxLayout()
        fila2.setSpacing(8)
        self._atajo = QKeySequenceEdit(QKeySequence(self._config.atajo), panel)
        self._atajo.setMaximumSequenceLength(1)
        self._atajo.editingFinished.connect(self._cambio_atajo)
        fila2.addWidget(self._atajo, 1)
        caja.addLayout(fila2)
        self._estado_atajo = QLabel("", panel)
        self._estado_atajo.setObjectName("suave")
        caja.addWidget(self._estado_atajo)

        # --- traductor -----------------------------------------------------
        caja.addWidget(self._etiqueta(
            "Traductor: clave de DeepL (opcional, gratis en deepl.com/pro-api)", panel))
        self._clave = QLineEdit(self._config.deepl_clave, panel)
        self._clave.setEchoMode(QLineEdit.Password)
        self._clave.setPlaceholderText("Vacio = se usa Google Translate")
        self._clave.editingFinished.connect(self._cambio_clave)
        caja.addWidget(self._clave)
        self._estado_clave = QLabel("", panel)
        self._estado_clave.setObjectName("suave")
        caja.addWidget(self._estado_clave)
        self._mostrar_estado_clave()

        # --- inicio con Windows --------------------------------------------
        self._inicio = QCheckBox("Iniciar con Windows", panel)
        self._inicio.setChecked(self._config.inicio_con_windows)
        self._inicio.toggled.connect(self._cambio_inicio)
        caja.addWidget(self._inicio)

        # --- pie -----------------------------------------------------------
        pie = QHBoxLayout()
        version = QLabel(f"version {APP_VERSION}", panel)
        version.setObjectName("suave")
        pie.addWidget(version)
        pie.addStretch(1)
        cerrar = QPushButton("Listo", panel)
        cerrar.setObjectName("principal")
        cerrar.clicked.connect(self.close)
        pie.addWidget(cerrar)
        caja.addLayout(pie)

        self.adjustSize()

    @staticmethod
    def _etiqueta(texto: str, padre: QWidget) -> QLabel:
        etiqueta = QLabel(texto, padre)
        etiqueta.setObjectName("suave")
        return etiqueta

    # ------------------------------------------------------------------ eventos
    def _elegir_carpeta(self) -> None:
        ruta = QFileDialog.getExistingDirectory(
            self, "Elegir la carpeta de capturas", self._config.carpeta_guardado
        )
        if ruta:
            self._config.carpeta_guardado = str(Path(ruta))
            self._carpeta.setText(self._config.carpeta_guardado)

    def _cambio_guardado(self, valor: bool) -> None:
        self._config.guardar_automatico = valor

    def _cambio_atajo(self) -> None:
        texto = self._atajo.keySequence().toString()
        if not texto:
            self._config.atajo = ""
            self._app.aplicar_atajo()
            self._estado_atajo.setText("Sin atajo: la barra se abre desde la bandeja.")
            return
        self._config.atajo = texto
        if self._app.aplicar_atajo():
            self._estado_atajo.setText(f"Atajo activo: {texto}")
        else:
            self._estado_atajo.setText(
                "Esa combinacion no se pudo registrar (puede estar usada por otro "
                "programa). Proba otra, con Ctrl, Alt o Shift."
            )

    def _cambio_clave(self) -> None:
        self._config.deepl_clave = self._clave.text()
        self._mostrar_estado_clave()

    def _mostrar_estado_clave(self) -> None:
        clave = self._config.deepl_clave
        if not clave:
            texto = "Sin clave: se usa Google Translate."
        elif clave.endswith(":fx"):
            texto = "Clave gratuita cargada: se usa DeepL (y Google si DeepL falla)."
        else:
            texto = "Clave cargada: se usa DeepL (y Google si DeepL falla)."
        self._estado_clave.setText(texto)

    def _cambio_inicio(self, valor: bool) -> None:
        from ..nucleo import inicio_windows

        if inicio_windows.aplicar(valor):
            self._config.inicio_con_windows = valor
        else:
            self._inicio.setChecked(not valor)
            self._app.ctx.avisar("No se pudo cambiar el inicio con Windows")

    def closeEvent(self, evento) -> None:  # noqa: N802, ANN001
        self._app.ventana_ajustes = None
        super().closeEvent(evento)
