# -*- coding: utf-8 -*-
"""
MOTORES DE TRADUCCION (espanol <-> ingles, y chino hacia cualquiera de los dos).

Dos motores, los dos con la libreria estandar de Python (urllib), asi que no
suman ninguna dependencia ni peso al .exe:

  - Google Translate: no necesita clave. Usa el endpoint que usa la propia
    pagina web, que NO es una API oficial: Google puede cambiarlo o limitar el
    uso sin aviso. Sirve para uso personal y liviano.
  - DeepL: necesita una clave gratuita (500.000 caracteres por mes) que se
    saca en https://www.deepl.com/pro-api . Es el motor preferido: si hay
    clave cargada se usa DeepL, y si falla se cae a Google.

Este modulo no sabe nada de Qt: recibe texto y devuelve texto.
"""

from __future__ import annotations

import json
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# AJUSTES
# ---------------------------------------------------------------------------
TIEMPO_ESPERA = 10          # segundos antes de darse por vencido
MAX_CARACTERES = 5000       # lo que pasa de esto se corta (cuida la cuota)
TAMANO_TROZO = 1200         # Google acepta pedidos cortos: se manda de a trozos
# Cuando el texto es chino y el destino esta en "auto", a que idioma se traduce:
# "es" (espanol) o "en" (ingles). En la ventana se puede forzar a mano.
IDIOMA_DESDE_CHINO = "es"

_AGENTE = "MToolBar/1.0"

NOMBRES_IDIOMA = {
    "en": "Ingles", "es": "Espanol", "zh": "Chino", "zh-CN": "Chino",
    "zh-TW": "Chino", "ja": "Japones", "ko": "Coreano", "fr": "Frances",
    "de": "Aleman", "pt": "Portugues", "it": "Italiano", "ru": "Ruso",
}


class ErrorTraduccion(Exception):
    """Algo salio mal; el mensaje esta listo para mostrarle al usuario."""


@dataclass
class Resultado:
    texto: str              # la traduccion
    motor: str              # "Google" o "DeepL"
    origen: str = ""        # idioma detectado ("en", "zh-CN"...), si se sabe
    destino: str = ""       # "en", "es" o "zh"
    nota: str = ""          # avisos: texto recortado, DeepL fallo, etc.

    @property
    def descripcion(self) -> str:
        """Ej.: 'Ingles -> Chino  -  DeepL'."""
        o = NOMBRES_IDIOMA.get(self.origen, self.origen.upper() or "Texto")
        d = NOMBRES_IDIOMA.get(self.destino, self.destino.upper())
        return f"{o} -> {d}  -  {self.motor}"


# ---------------------------------------------------------------------------
# DETECCION DE IDIOMA (solo lo justo para decidir el destino)
# ---------------------------------------------------------------------------
def _es_ideograma(c: str) -> bool:
    o = ord(c)
    return (0x4E00 <= o <= 0x9FFF or 0x3400 <= o <= 0x4DBF
            or 0xF900 <= o <= 0xFAFF or 0x20000 <= o <= 0x2A6DF)


# Palabras muy comunes de cada idioma: alcanzan para distinguir espanol de ingles.
# Las que existen en los dos (no, a, me...) se dejaron afuera a proposito.
_PALABRAS_ES = frozenset(
    "el la los las de que y en un una es por con para se del al lo como pero su "
    "le ya o este esta esto entre cuando muy sin sobre tambien hasta hay donde "
    "desde todo nos todos les ni otro otra eso ese estoy tengo soy eres somos "
    "hola gracias buenos dias favor quiero necesito puedo puede esta estan".split()
)
_PALABRAS_EN = frozenset(
    "the of and to in is you that it he was for on are as with his they i at be "
    "this have from or one had by but what all were we when your can there an "
    "each which she do how their if will up other about out many then them these "
    "so some her would make like him into has more could my than been who its "
    "hello thanks please just am does".split()
)
_LETRAS = re.compile(r"[a-záéíóúüñ]+")


def _idioma_latino(texto: str) -> str:
    """'es', 'en' o '' si no hay forma de saberlo (una palabra suelta, por ej.)."""
    minuscula = texto.lower()
    palabras = _LETRAS.findall(minuscula)
    puntos_es = sum(1 for p in palabras if p in _PALABRAS_ES)
    puntos_en = sum(1 for p in palabras if p in _PALABRAS_EN)
    # Las tildes, la enie y los signos de apertura son casi seguro espanol.
    puntos_es += 2 * sum(1 for c in minuscula if c in "áéíóúñ¿¡")
    if puntos_es > puntos_en:
        return "es"
    if puntos_en > puntos_es:
        return "en"
    return ""


def adivinar_destino(texto: str) -> str:
    """
    A que idioma conviene traducir este texto:
      chino   -> IDIOMA_DESDE_CHINO (espanol por defecto)
      espanol -> ingles
      ingles  -> espanol
    Es una primera suposicion barata; si falla, traducir() lo corrige solo.
    """
    letras = [c for c in texto if c.isalpha()]
    if letras and sum(1 for c in letras if _es_ideograma(c)) / len(letras) >= 0.3:
        return IDIOMA_DESDE_CHINO
    return "es" if _idioma_latino(texto) == "en" else "en"


# ---------------------------------------------------------------------------
# UTILIDADES
# ---------------------------------------------------------------------------
def _trozos(texto: str, limite: int = TAMANO_TROZO) -> list[str]:
    """Parte el texto por renglones en pedazos de hasta `limite` caracteres."""
    salida: list[str] = []
    actual = ""
    for linea in texto.splitlines(keepends=True):
        while len(linea) > limite:          # un renglon gigante se corta a la fuerza
            if actual:
                salida.append(actual)
                actual = ""
            salida.append(linea[:limite])
            linea = linea[limite:]
        if actual and len(actual) + len(linea) > limite:
            salida.append(actual)
            actual = ""
        actual += linea
    if actual.strip():
        salida.append(actual)
    return salida


def _pedir(solicitud: urllib.request.Request) -> object:
    """Hace el pedido HTTP y devuelve el JSON, con errores en castellano."""
    try:
        with urllib.request.urlopen(solicitud, timeout=TIEMPO_ESPERA) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise ErrorTraduccion(_mensaje_http(e.code)) from e
    except (socket.timeout, TimeoutError) as e:
        raise ErrorTraduccion("El servicio tardo demasiado en responder.") from e
    except urllib.error.URLError as e:
        if isinstance(e.reason, (socket.timeout, TimeoutError)):
            raise ErrorTraduccion("El servicio tardo demasiado en responder.") from e
        raise ErrorTraduccion("No hay conexion a internet.") from e
    except (ValueError, UnicodeDecodeError) as e:
        raise ErrorTraduccion("El servicio respondio algo inesperado.") from e


def _mensaje_http(codigo: int) -> str:
    return {
        400: "El servicio rechazo el pedido.",
        403: "La clave de DeepL no es valida.",
        429: "Demasiados pedidos seguidos: espera un momento.",
        456: "Se agoto la cuota mensual de DeepL.",
        503: "El servicio no esta disponible ahora.",
    }.get(codigo, f"El servicio respondio con un error ({codigo}).")


# ---------------------------------------------------------------------------
# GOOGLE
# ---------------------------------------------------------------------------
def _leer_google(datos: object) -> tuple[str, str]:
    """Extrae (texto traducido, idioma detectado) de la respuesta de Google."""
    try:
        segmentos = datos[0]                                    # type: ignore[index]
        texto = "".join(s[0] for s in segmentos if s and s[0])
        origen = datos[2] if len(datos) > 2 and isinstance(datos[2], str) else ""  # type: ignore[arg-type,index]
    except (TypeError, IndexError, KeyError) as e:
        raise ErrorTraduccion("Google respondio algo que no se entiende.") from e
    return texto, origen


def _google(texto: str, destino: str, origen: str = "auto") -> Resultado:
    tl = "zh-CN" if destino == "zh" else destino
    partes: list[str] = []
    idioma_detectado = ""
    for trozo in _trozos(texto):
        consulta = urllib.parse.urlencode(
            {"client": "gtx", "sl": origen, "tl": tl, "dt": "t", "q": trozo}
        )
        url = "https://translate.googleapis.com/translate_a/single?" + consulta
        pedido = urllib.request.Request(url, headers={"User-Agent": _AGENTE})
        traducido, detectado = _leer_google(_pedir(pedido))
        partes.append(traducido)
        idioma_detectado = idioma_detectado or detectado
    return Resultado("".join(partes), "Google", idioma_detectado, destino)


# ---------------------------------------------------------------------------
# DEEPL
# ---------------------------------------------------------------------------
def _leer_deepl(datos: object) -> tuple[str, str]:
    """Extrae (texto traducido, idioma detectado) de la respuesta de DeepL."""
    try:
        lista = datos["translations"]                           # type: ignore[index]
        texto = "".join(t["text"] for t in lista)
        origen = lista[0].get("detected_source_language", "").lower()
    except (TypeError, IndexError, KeyError, AttributeError) as e:
        raise ErrorTraduccion("DeepL respondio algo que no se entiende.") from e
    return texto, origen


def _deepl(texto: str, destino: str, clave: str, origen: str = "auto") -> Resultado:
    # Las claves gratuitas terminan en ":fx" y usan otro servidor que las de pago.
    base = "api-free.deepl.com" if clave.endswith(":fx") else "api.deepl.com"
    campos = {
        "text": _trozos(texto),
        "target_lang": {"zh": "ZH", "en": "EN-US", "es": "ES"}.get(destino, destino.upper()),
    }
    if origen != "auto":
        campos["source_lang"] = origen.upper()
    cuerpo = json.dumps(campos).encode("utf-8")
    pedido = urllib.request.Request(
        f"https://{base}/v2/translate", data=cuerpo, method="POST",
        headers={
            "Authorization": f"DeepL-Auth-Key {clave}",
            "Content-Type": "application/json",
            "User-Agent": _AGENTE,
        },
    )
    traducido, origen = _leer_deepl(_pedir(pedido))
    return Resultado(traducido, "DeepL", origen, destino)


# ---------------------------------------------------------------------------
# PUNTO DE ENTRADA
# ---------------------------------------------------------------------------
def _una_vez(texto: str, destino: str, clave: str, origen: str = "auto") -> Resultado:
    """Un pedido: DeepL si hay clave (y si falla, Google), o Google directo."""
    if clave:
        try:
            return _deepl(texto, destino, clave, origen)
        except ErrorTraduccion as error:
            resultado = _google(texto, destino, origen)
            resultado.nota = f"DeepL fallo ({error}) Se uso Google."
            return resultado
    return _google(texto, destino, origen)


def traducir(texto: str, clave_deepl: str = "", destino: str = "auto") -> Resultado:
    """
    Traduce `texto`.

    destino: "es", "en", "zh", o "auto" (espanol <-> ingles; chino -> espanol).
    Con clave de DeepL intenta DeepL primero y, si falla, usa Google avisandolo
    en `nota`. Puede levantar ErrorTraduccion.
    """
    texto = texto.strip()
    if not texto:
        raise ErrorTraduccion("No hay texto para traducir.")

    aviso = ""
    if len(texto) > MAX_CARACTERES:
        texto = texto[:MAX_CARACTERES]
        aviso = f"Se tradujeron solo los primeros {MAX_CARACTERES} caracteres."

    clave = clave_deepl.strip()
    automatico = destino == "auto"
    if automatico:
        destino = adivinar_destino(texto)

    resultado = _una_vez(texto, destino, clave)

    # En automatico, si el servicio dice que el texto YA estaba en el idioma al
    # que lo mandamos (la suposicion fallo), se da vuelta: espanol <-> ingles.
    if automatico and resultado.origen.split("-")[0] == destino and destino in ("es", "en"):
        otro = "en" if destino == "es" else "es"
        nuevo = _una_vez(texto, otro, clave)
        nuevo.nota = " ".join(p for p in (resultado.nota, nuevo.nota) if p)
        resultado = nuevo

    # Ultimo recurso: si volvio identico, el servicio no supo ubicar el idioma
    # (le pasa a palabras sueltas como "casa", que Google cree que es ingles).
    # Se fuerza el origen: "esto esta en <destino>, pasalo al otro idioma".
    if (automatico and resultado.destino in ("es", "en")
            and resultado.texto.strip().casefold() == texto.casefold()):
        de = resultado.destino
        forzado = _una_vez(texto, "en" if de == "es" else "es", clave, origen=de)
        if forzado.texto.strip().casefold() != texto.casefold():
            forzado.origen = de
            forzado.nota = " ".join(p for p in (resultado.nota, forzado.nota) if p)
            resultado = forzado

    resultado.nota = " ".join(p for p in (resultado.nota, aviso) if p)
    return resultado
