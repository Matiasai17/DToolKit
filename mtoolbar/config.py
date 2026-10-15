# -*- coding: utf-8 -*-
"""
Preferencias del usuario, guardadas en el registro de Windows con QSettings
(HKCU -> Software -> MToolBar). No hace falta ningun archivo suelto.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QSettings, QStandardPaths, Signal

from . import APP_NOMBRE

# Valores por defecto la primera vez que se abre la app.
ATAJO_POR_DEFECTO = "Ctrl+Shift+Space"


def _carpeta_imagenes_por_defecto() -> str:
    base = QStandardPaths.writableLocation(QStandardPaths.PicturesLocation)
    return str(Path(base) / APP_NOMBRE)


class Config(QObject):
    """Acceso tipado a las preferencias. Emite `cambio` cuando algo se guarda."""

    cambio = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._s = QSettings(APP_NOMBRE, APP_NOMBRE)

    # --- carpeta donde se guardan las capturas -----------------------------
    @property
    def carpeta_guardado(self) -> str:
        return self._s.value("carpeta_guardado", _carpeta_imagenes_por_defecto(), str)

    @carpeta_guardado.setter
    def carpeta_guardado(self, valor: str) -> None:
        self._s.setValue("carpeta_guardado", valor)
        self.cambio.emit()

    # --- guardar el PNG automaticamente o solo copiar al portapapeles ------
    @property
    def guardar_automatico(self) -> bool:
        return self._s.value("guardar_automatico", True, bool)

    @guardar_automatico.setter
    def guardar_automatico(self, valor: bool) -> None:
        self._s.setValue("guardar_automatico", bool(valor))
        self.cambio.emit()

    # --- atajo global para abrir la barra ----------------------------------
    @property
    def atajo(self) -> str:
        return self._s.value("atajo", ATAJO_POR_DEFECTO, str)

    @atajo.setter
    def atajo(self, valor: str) -> None:
        self._s.setValue("atajo", valor)
        self.cambio.emit()

    # --- arrancar junto con Windows ---------------------------------------
    @property
    def inicio_con_windows(self) -> bool:
        return self._s.value("inicio_con_windows", False, bool)

    @inicio_con_windows.setter
    def inicio_con_windows(self, valor: bool) -> None:
        self._s.setValue("inicio_con_windows", bool(valor))
        self.cambio.emit()

    # --- clave de DeepL para el traductor (vacia = se usa Google) ----------
    # Queda guardada tal cual en el registro de Windows del usuario.
    @property
    def deepl_clave(self) -> str:
        return self._s.value("deepl_clave", "", str)

    @deepl_clave.setter
    def deepl_clave(self, valor: str) -> None:
        self._s.setValue("deepl_clave", valor.strip())
        self.cambio.emit()

    def asegurar_carpeta(self) -> Path:
        """Crea la carpeta de guardado si no existe y devuelve su ruta."""
        ruta = Path(self.carpeta_guardado)
        ruta.mkdir(parents=True, exist_ok=True)
        return ruta
