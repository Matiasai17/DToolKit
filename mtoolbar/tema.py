# -*- coding: utf-8 -*-
"""
TEMA / DISENO  -  el unico archivo que necesitas tocar para cambiar el aspecto.

Todo lo visual de la app sale de aca: colores, tamanos, tipografia, radios de
borde y opacidades. Ningun otro archivo define colores ni medidas.

Los colores se escriben en formato "#RRGGBB" o "#AARRGGBB" (el AA del principio
es la transparencia: 00 = invisible, FF = opaco).
"""

# ---------------------------------------------------------------------------
# PALETA
# ---------------------------------------------------------------------------
# Fondo de la barra flotante. El "E6" del principio es la transparencia (90%).
COLOR_FONDO_BARRA = "#E6202124"
# Borde fino alrededor de la barra (dale "#00000000" para que no se vea).
COLOR_BORDE_BARRA = "#33FFFFFF"
# Color de los iconos en reposo y cuando pasas el mouse.
COLOR_ICONO = "#F2F2F2"
COLOR_ICONO_HOVER = "#FFFFFF"
# Fondo del boton cuando pasas el mouse por encima / cuando lo apretas.
COLOR_BOTON_HOVER = "#2AFFFFFF"
COLOR_BOTON_ACTIVO = "#45FFFFFF"
# Color de acento: rectangulo de seleccion, foco, boton principal.
COLOR_ACENTO = "#4CA3FF"
# Ventanas (resultado del codigo, ajustes).
COLOR_FONDO_VENTANA = "#F22A2B2F"
COLOR_TEXTO = "#F2F2F2"
COLOR_TEXTO_SUAVE = "#9AA0A6"
# Avisos tipo "Copiado".
COLOR_FONDO_AVISO = "#F2202124"
COLOR_TEXTO_AVISO = "#FFFFFF"
# Overlay de seleccion de area: oscurecido de la pantalla congelada.
COLOR_OSCURECER = "#59000000"   # 59 = 35% de negro

# ---------------------------------------------------------------------------
# TIPOGRAFIA
# ---------------------------------------------------------------------------
FUENTE = "Segoe UI"
TAMANO_TEXTO = 10          # puntos
TAMANO_TEXTO_CHICO = 9
TAMANO_TEXTO_TITULO = 12

# ---------------------------------------------------------------------------
# MEDIDAS DE LA BARRA FLOTANTE
# ---------------------------------------------------------------------------
RADIO_BARRA = 12           # redondeo de las esquinas, en pixeles
GROSOR_BORDE_BARRA = 1
PADDING_BARRA = 6          # aire interno entre el borde y los botones
ESPACIO_BOTONES = 2        # separacion entre botones
TAMANO_BOTON = 40          # alto y ancho de cada boton
TAMANO_ICONO = 20          # tamano del dibujo dentro del boton
RADIO_BOTON = 8

# DONDE APARECE LA BARRA. Opciones:
#   "abajo-derecha"   "abajo-centro"   "abajo-izquierda"
#   "arriba-derecha"  "arriba-centro"  "arriba-izquierda"
#   "centro"          "mouse"  (justo donde esta el puntero)
POSICION_BARRA = "abajo-derecha"
# Distancia a los bordes de la pantalla, en pixeles.
MARGEN_PANTALLA_X = 18
MARGEN_PANTALLA_Y = 18
# Separador vertical entre grupos de botones (ver GRUPOS en la barra).
ANCHO_SEPARADOR = 1
COLOR_SEPARADOR = "#26FFFFFF"

# ---------------------------------------------------------------------------
# MEDIDAS DE VENTANAS Y AVISOS
# ---------------------------------------------------------------------------
RADIO_VENTANA = 12
PADDING_VENTANA = 16
RADIO_AVISO = 8
PADDING_AVISO_H = 14
PADDING_AVISO_V = 9
# Cuanto tiempo queda visible el aviso "Copiado", en milisegundos.
DURACION_AVISO_MS = 1500
# Duracion de la animacion de aparicion/desaparicion, en milisegundos.
DURACION_FUNDIDO_MS = 140

# ---------------------------------------------------------------------------
# OVERLAY DE SELECCION
# ---------------------------------------------------------------------------
GROSOR_SELECCION = 2       # grosor del borde del rectangulo de seleccion
GROSOR_GUIAS = 1           # grosor de la cruz de guia
COLOR_GUIAS = "#66FFFFFF"
MOSTRAR_GUIAS = True       # ponelo en False si no queres la cruz
MOSTRAR_MEDIDAS = True     # el cartelito con "800 x 600"


def _qss_ventana() -> str:
    """Estilos de las ventanas comunes (resultado, ajustes)."""
    return f"""
    QWidget#panel {{
        background-color: {COLOR_FONDO_VENTANA};
        border: {GROSOR_BORDE_BARRA}px solid {COLOR_BORDE_BARRA};
        border-radius: {RADIO_VENTANA}px;
    }}
    QLabel {{
        color: {COLOR_TEXTO};
        font-family: "{FUENTE}";
        font-size: {TAMANO_TEXTO}pt;
        background: transparent;
    }}
    QLabel#titulo {{
        font-size: {TAMANO_TEXTO_TITULO}pt;
        font-weight: 600;
    }}
    QLabel#suave {{
        color: {COLOR_TEXTO_SUAVE};
        font-size: {TAMANO_TEXTO_CHICO}pt;
    }}
    QPlainTextEdit, QLineEdit {{
        background-color: #1A000000;
        color: {COLOR_TEXTO};
        border: 1px solid {COLOR_BORDE_BARRA};
        border-radius: {RADIO_BOTON}px;
        padding: 8px;
        font-family: "{FUENTE}";
        font-size: {TAMANO_TEXTO}pt;
        selection-background-color: {COLOR_ACENTO};
    }}
    QPushButton {{
        background-color: {COLOR_BOTON_HOVER};
        color: {COLOR_TEXTO};
        border: none;
        border-radius: {RADIO_BOTON}px;
        padding: 7px 16px;
        font-family: "{FUENTE}";
        font-size: {TAMANO_TEXTO}pt;
    }}
    QPushButton:hover {{ background-color: {COLOR_BOTON_ACTIVO}; }}
    QPushButton#principal {{
        background-color: {COLOR_ACENTO};
        color: #0B1A2B;
        font-weight: 600;
    }}
    QPushButton#principal:hover {{ background-color: {COLOR_ICONO_HOVER}; }}
    QPushButton#idioma {{
        background-color: transparent;
        border: 1px solid {COLOR_BORDE_BARRA};
        padding: 4px 12px;
        font-size: {TAMANO_TEXTO_CHICO}pt;
    }}
    QPushButton#idioma:hover {{ background-color: {COLOR_BOTON_HOVER}; }}
    QPushButton#idioma:checked {{
        background-color: {COLOR_ACENTO};
        border-color: {COLOR_ACENTO};
        color: #0B1A2B;
        font-weight: 600;
    }}
    QCheckBox {{
        color: {COLOR_TEXTO};
        font-family: "{FUENTE}";
        font-size: {TAMANO_TEXTO}pt;
        spacing: 8px;
        background: transparent;
    }}
    QToolTip {{
        background-color: {COLOR_FONDO_AVISO};
        color: {COLOR_TEXTO_AVISO};
        border: 1px solid {COLOR_BORDE_BARRA};
        border-radius: 6px;
        padding: 4px 8px;
        font-family: "{FUENTE}";
        font-size: {TAMANO_TEXTO_CHICO}pt;
    }}
    """


def _qss_barra() -> str:
    """Estilos de la barra flotante y sus botones."""
    return f"""
    QToolButton#herramienta {{
        background-color: transparent;
        border: none;
        border-radius: {RADIO_BOTON}px;
        min-width: {TAMANO_BOTON}px;
        min-height: {TAMANO_BOTON}px;
    }}
    QToolButton#herramienta:hover {{ background-color: {COLOR_BOTON_HOVER}; }}
    QToolButton#herramienta:pressed {{ background-color: {COLOR_BOTON_ACTIVO}; }}
    QFrame#separador {{ background-color: {COLOR_SEPARADOR}; border: none; }}
    """


def qss() -> str:
    """Hoja de estilos completa que se aplica a toda la app."""
    return _qss_barra() + _qss_ventana()
