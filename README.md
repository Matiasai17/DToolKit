# MToolBar

Un toolkit de herramientas rápidas que vive en la bandeja del sistema de Windows
(al lado del reloj). Un click en el ícono abre una barra flotante chica —abajo a la
derecha, cerca del reloj— con un botón por herramienta.

Herramientas actuales:

| | Herramienta | Qué hace |
|---|---|---|
| 1 | **Captura de pantalla** | Oscurece la pantalla, seleccionás un área, la copia al portapapeles y la guarda como PNG. |
| 2 | **Lector de QR y códigos de barras** | Seleccionás un área de la pantalla (o cargás una imagen) y te muestra el contenido con botones Copiar y Abrir. |
| 3 | **Traductor** | Copiás un texto, apretás `3` y aparece traducido: español ↔ inglés, y chino → español o inglés. Usa Google Translate o DeepL. |

---

## 1. Cómo ejecutarla

**Doble click en `run.bat`.**

La primera vez tarda unos minutos: prepara una carpeta `.venv` con Python y las
dos librerías que usa. Después arranca en un segundo.

No se abre ninguna ventana: aparece el ícono en la bandeja del sistema. Si no lo
ves, hacé click en la flechita `^` de la barra de tareas y arrastrá el ícono de
MToolBar hacia afuera para que quede siempre visible.

### Cómo se usa

- **Click en el ícono de la bandeja** → se abre la barra flotante abajo a la derecha
  (se cambia con `POSICION_BARRA` en `tema.py`).
- **`Ctrl + Shift + Espacio`** → lo mismo, sin tocar el mouse (se puede cambiar en Ajustes).
- **`Esc` o click afuera** → la barra se cierra.
- **Teclas `1`, `2` y `3`** mientras la barra está abierta → activan cada herramienta.
- **Click derecho en un botón** → acciones extra de esa herramienta (por ejemplo
  "Leer desde una imagen..." o "Capturar el monitor completo").
- **Click derecho en el ícono de la bandeja** → menú con todo, Ajustes y Salir.

### En el selector de área

- **Arrastrar** → selecciona ese rectángulo.
- **Enter** o **doble click** → el monitor completo.
- **Esc** o **click derecho** → cancelar.

### Ajustes

Botón de la derecha en la barra, o click derecho en la bandeja → *Ajustes*:

- Carpeta donde se guardan las capturas (por defecto `Imágenes\MToolBar`).
- Guardar el PNG automáticamente, o solo copiar al portapapeles.
- El atajo de teclado global (hacé click en el campo y apretá la combinación).
- Iniciar con Windows.

---

### El traductor

1. Copiá el texto en cualquier programa (`Ctrl+C`).
2. Abrí la barra (`Ctrl+Shift+Espacio`) y apretá **`3`**.
3. La ventana aparece con la traducción ya hecha. **Copiar traducción** la deja
   en el portapapeles para pegarla.

El idioma destino se elige solo:

| Si el texto está en… | se traduce a… |
|---|---|
| español | inglés |
| inglés | español |
| chino | español |

Con los botones **Auto · Español · Inglés · Chino** lo forzás a mano (por
ejemplo, chino → inglés, o español → chino). También podés escribir o pegar
directamente en la ventana y apretar **Traducir** (`Ctrl+Enter`).

Si preferís que el chino vaya a inglés por defecto, cambiá
`IDIOMA_DESDE_CHINO = "es"` por `"en"` en
[`mtoolbar/nucleo/traduccion.py`](mtoolbar/nucleo/traduccion.py).

#### Google o DeepL

- **Sin hacer nada** se usa **Google Translate**. No pide clave ni cuenta. Ojo:
  usa el mismo acceso que la página web de Google, que **no es una API
  oficial**: anda bien para uso personal, pero Google lo puede cambiar o limitar
  sin aviso. A veces se come alguna tilde ("esta" en vez de "está").
- **DeepL** traduce mejor, sobre todo al español, y es gratis hasta **500.000
  caracteres por mes** (son cientos de páginas). Para activarlo:
  1. Entrá a <https://www.deepl.com/pro-api> y elegí el plan **DeepL API Free**.
  2. Creá la cuenta. DeepL puede pedirte una tarjeta solo para verificar que
     sos una persona; el plan Free no cobra.
  3. En tu cuenta, entrá a **Claves API** y copiá la clave (las gratuitas
     terminan en `:fx`).
  4. En MToolBar: **Ajustes → Traductor → pegá la clave**.

  Con clave cargada se usa DeepL, y si DeepL falla (se agotó la cuota del mes,
  la clave dejó de valer, no responde) la app **usa Google sola** y te lo avisa
  debajo de la traducción.

#### Privacidad

El texto que traducís **viaja a Google o a DeepL** para ser traducido: no lo
uses con contraseñas ni datos sensibles. La clave de DeepL queda guardada sin
cifrar en el registro de Windows de tu usuario (`HKEY_CURRENT_USER\Software\MToolBar`).

---

## 2. Cómo cambiar el diseño

Todo lo visual está en **un solo archivo**: [`mtoolbar/tema.py`](mtoolbar/tema.py).
Lo abrís con el Bloc de notas (o cualquier editor), cambiás los valores, guardás y
volvés a abrir la app. No hace falta compilar nada.

Los colores se escriben como `"#RRGGBB"` o `"#AARRGGBB"`, donde `AA` es la
transparencia en hexadecimal (`00` = invisible, `80` ≈ 50%, `FF` = opaco).

### Lo que más vas a querer tocar

| Constante | Qué afecta |
|---|---|
| `COLOR_FONDO_BARRA` | Fondo de la barra flotante (con transparencia). |
| `COLOR_BORDE_BARRA` | El borde fino de la barra. Poné `"#00000000"` para que no se vea. |
| `COLOR_ICONO` / `COLOR_ICONO_HOVER` | Color de los íconos, normal y al pasar el mouse. |
| `COLOR_BOTON_HOVER` | Fondo del botón al pasar el mouse. |
| `COLOR_ACENTO` | Rectángulo de selección y botón principal. |
| `RADIO_BARRA` | Redondeo de las esquinas de la barra, en píxeles. |
| `TAMANO_BOTON` / `TAMANO_ICONO` | Tamaño de los botones y del dibujo adentro. |
| `PADDING_BARRA` / `ESPACIO_BOTONES` | Aire interno y separación entre botones. |
| `POSICION_BARRA` | **Dónde aparece la barra.** Por defecto `"abajo-derecha"`. Las otras opciones son `"abajo-centro"`, `"abajo-izquierda"`, `"arriba-derecha"`, `"arriba-centro"`, `"arriba-izquierda"`, `"centro"` y `"mouse"` (justo donde está el puntero). |
| `MARGEN_PANTALLA_X` / `MARGEN_PANTALLA_Y` | Distancia a los bordes de la pantalla. La barra de tareas ya se descuenta sola. |
| `FUENTE` / `TAMANO_TEXTO` | Tipografía de toda la app (cualquier fuente instalada). |
| `COLOR_OSCURECER` | Cuánto se oscurece la pantalla al seleccionar un área. |
| `MOSTRAR_GUIAS` / `MOSTRAR_MEDIDAS` | La cruz que sigue al mouse y el cartelito de "800 x 600". |
| `DURACION_AVISO_MS` | Cuánto queda en pantalla el aviso "Copiado". |

Al final del archivo está la función `qss()`, que es la hoja de estilos (CSS de Qt)
de las ventanas y los botones. Si querés tocar algo más fino —padding de los
botones, bordes de los campos de texto— está todo ahí y usa las mismas constantes.

### Cambiar los íconos

Están en [`mtoolbar/recursos/iconos/`](mtoolbar/recursos/iconos) como SVG de 24×24.
Reemplazá el archivo por el tuyo, con el mismo nombre, y listo.

Dos cosas a tener en cuenta:

- **El color del SVG no importa**: la app lo recolorea sola con `COLOR_ICONO`.
  Diseñalos en un solo color (negro está bien) y con fondo transparente.
- Conviene usar **trazos** (`stroke`) de 1.5–2 px en un `viewBox="0 0 24 24"`,
  como los actuales, para que todos se vean parejos.

Archivos: `captura.svg`, `codigos.svg`, `traducir.svg`, `ajustes.svg`, `imagen.svg` y `app.svg`
(este último es el de la bandeja y, con fondo, el del `.exe`).

---

## 3. Cómo agregar una herramienta nueva

Tres pasos. No hay que tocar la barra, ni la bandeja, ni nada del núcleo.

**Paso 1** — Creá el archivo `mtoolbar/herramientas/color.py`:

```python
# -*- coding: utf-8 -*-
"""HERRAMIENTA: cuentagotas (copia el color de un píxel de la pantalla)."""

from ..nucleo.herramienta import Herramienta, registrar


@registrar
class Cuentagotas(Herramienta):
    id = "color"                      # identificador interno, sin espacios
    nombre = "Copiar un color"        # lo que dice el tooltip
    icono = "color.svg"               # archivo dentro de recursos/iconos
    atajo_local = "3"                 # tecla mientras la barra está abierta
    orden = 30                        # posición en la barra (menor = más a la izquierda)

    def ejecutar(self, ctx):
        imagen = ctx.seleccionar_area()      # None si el usuario canceló
        if imagen is None:
            return
        color = imagen.toImage().pixelColor(0, 0)
        ctx.copiar_texto(color.name().upper())   # por ejemplo "#3F7AD4"
        ctx.avisar(f"Copiado {color.name().upper()}")
```

**Paso 2** — Poné tu `color.svg` en `mtoolbar/recursos/iconos/`.

**Paso 3** — Agregá una línea en `mtoolbar/herramientas/__init__.py`:

```python
from . import color   # noqa: F401
```

Volvés a abrir la app y el botón ya está en la barra, que se ensancha sola.

### Lo que podés usar desde `ctx`

| Llamada | Qué hace |
|---|---|
| `ctx.seleccionar_area()` | Abre el selector y devuelve la imagen (`None` si se canceló). |
| `ctx.capturar_pantalla_completa()` | Captura el monitor donde está el mouse. |
| `ctx.abrir_archivo_imagen()` | Diálogo para elegir una imagen del disco. |
| `ctx.copiar_imagen(imagen)` / `ctx.copiar_texto(texto)` | Portapapeles. |
| `ctx.guardar_png(imagen, "Prefijo")` | Guarda en la carpeta configurada y devuelve la ruta. |
| `ctx.avisar("Copiado")` | El avisito flotante. |
| `ctx.abrir_url(url)` / `ctx.abrir_carpeta(ruta)` | Abre el navegador o el explorador. |
| `ctx.config` | Las preferencias del usuario. |

Y si querés acciones extra en el click derecho del botón, agregá esto a tu clase:

```python
    def acciones_extra(self, ctx):
        return [("Hacer otra cosa...", lambda: self._otra_cosa(ctx))]
```

Una aclaración: `cerrar_barra_antes = True` (el valor por defecto) hace que la
barra se esconda antes de ejecutar la herramienta, que es lo que querés para
cualquier cosa que capture la pantalla. Si tu herramienta solo abre una ventana,
podés poner `cerrar_barra_antes = False`.

---

## 4. Cómo generar el `.exe`

**Doble click en `build.bat`** y esperar (la primera vez, varios minutos).

Cuando termina queda **`dist\MToolBar.exe`**: un único archivo portable de
**27 MB**. Lo copiás a donde quieras —otra carpeta, un pendrive, otra PC con
Windows— y funciona solo, sin instalar Python ni nada.

El script hace tres cosas más por su cuenta: regenera el ícono del ejecutable a
partir de `app.svg` (si cambiás ese SVG, el `.exe` sale con tu ícono nuevo),
recorta de Qt todo lo que la app no usa, y al final **corre una autoprueba sobre
el `.exe` ya generado** para confirmar que el recorte no se pasó de rosca. El
resultado también queda en `dist\autoprueba.txt`:

```
[OK]    Qt: PySide6 6.12.0, plataforma 'windows', 2 monitor(es)
[OK]    Iconos SVG: captura.svg -> 20x20 px
[OK]    Barra de herramientas: 3 herramientas, barra de 181x52 px
[OK]    Lector de codigos: QRCode, EAN13, Code128
[OK]    Captura de pantalla: recorte de 120x80 px
[OK]    Portapapeles: escribe y lee
[OK]    Atajo global: Ctrl+Alt+F9 registrado y liberado
[OK]    Traductor (local): respuestas de Google y DeepL, es->en, en->es, zh->es
[OK]    Traductor (internet): 'Hola, buenos dias' -> 'Hello good morning' (Google)
[OK]    Bandeja del sistema: disponible
TODO OK
```

La prueba del traductor por internet es la única que necesita conexión: si no
hay red, aparece como `[AVISO]` y no cuenta como falla.

La podés correr vos cuando quieras: `dist\MToolBar.exe --autoprueba`.

### Qué se recorta, y dónde se toca

PyInstaller, por las dudas, mete **todo** Qt: el motor web, Qt Quick, OpenGL por
software, OpenSSL… unos 150 MB de los cuales la app usa una fracción. La receta
que deja solo lo necesario está en [`MToolBar.spec`](MToolBar.spec), comentada.
Arriba de todo tiene dos cosas que te pueden interesar:

```python
UN_SOLO_ARCHIVO = True      # False = una carpeta dist\MToolBar\ que arranca al instante
MODULOS_QT = {"QtCore", "QtGui", "QtWidgets", "QtSvg"}
```

Si algún día agregás una herramienta que necesite un módulo de Qt nuevo —por
ejemplo `QtMultimedia` para la cámara— sumalo a `MODULOS_QT` y a
`BIBLIOTECAS_QT`, cambiá `PySide6-Essentials` por `PySide6` en
`requirements.txt`, y corré la autoprueba para confirmar que quedó bien.

Dos detalles más:

- La primera vez que lo abrís, Windows puede mostrar un cartel azul de
  "Windows protegió tu PC" porque el `.exe` no tiene firma digital. Es
  *Más información* → *Ejecutar de todas formas*. Pasa con cualquier programa
  no firmado; firmarlo cuesta plata y no hace falta para uso propio.
- Un `.exe` de un solo archivo se descomprime en una carpeta temporal al
  arrancar, así que la primera vez tarda 1 o 2 segundos más. Si te molesta,
  poné `UN_SOLO_ARCHIVO = False` en el `.spec`: queda una carpeta en vez de un
  archivo, pero arranca al instante.

---

## 5. Cómo está armado (por si querés meter mano)

```
QR-Bar/
├── run.bat                    doble click para ejecutar
├── build.bat                  doble click para generar el .exe
├── MToolBar.spec              receta del empaquetado (qué entra y qué no)
├── ejecutar.py                punto de entrada
├── requirements.txt           las dos librerías que usa
├── mtoolbar/
│   ├── tema.py                ★ TODO EL DISEÑO
│   ├── config.py              preferencias del usuario
│   ├── __main__.py            arranque: une bandeja + barra + atajo
│   ├── autoprueba.py          el chequeo que corre build.bat al final
│   ├── nucleo/                lo que las herramientas reutilizan
│   │   ├── herramienta.py     el contrato: clase base + registro
│   │   ├── contexto.py        la caja de herramientas que recibe cada módulo
│   │   ├── barra.py           la barra flotante
│   │   ├── bandeja.py         el ícono de la bandeja y su menú
│   │   ├── selector.py        el overlay para seleccionar un área
│   │   ├── pantalla.py        capturar y recortar monitores
│   │   ├── aviso.py           el avisito "Copiado"
│   │   ├── iconos.py          carga los SVG y los pinta con el color del tema
│   │   ├── traduccion.py      motores del traductor (Google y DeepL)
│   │   ├── atajo.py           el atajo de teclado global
│   │   └── inicio_windows.py  iniciar con Windows
│   ├── herramientas/          ★ una herramienta por archivo
│   ├── ventanas/              ventanas de resultado, traductor y ajustes
│   └── recursos/iconos/       ★ los SVG
└── utiles/generar_ico.py      genera el ícono del .exe desde app.svg
```

Las librerías son solo dos:

- **PySide6-Essentials** (Qt para Python, sin el motor web ni Qt Quick): la
  interfaz, la bandeja, la captura de pantalla y el portapapeles.
- **zxing-cpp**: el decodificador de códigos. Soporta QR, Micro QR, DataMatrix,
  Aztec, PDF417, EAN-13, EAN-8, UPC-A, UPC-E, Code 128, Code 39, Code 93, ITF,
  Codabar y DataBar.

El atajo global no usa ninguna librería: le habla directo a Windows
(`RegisterHotKey`), así que no necesita permisos de administrador.

### Dónde quedan las preferencias

En el registro de Windows, en `HKEY_CURRENT_USER\Software\MToolBar`. Si querés
dejar la PC como estaba: desactivá "Iniciar con Windows" en Ajustes, salí de la
app y borrá esa clave con `regedit`.

---

## 6. Si algo no funciona

| Síntoma | Qué pasa |
|---|---|
| El atajo `Ctrl+Shift+Espacio` no hace nada | Otro programa lo tiene tomado. Cambialo en Ajustes: si la combinación no se pudo registrar, te lo avisa ahí mismo. |
| "No se encontró ningún código" | Seleccioná un poco más de margen alrededor del código, o agrandá la imagen en pantalla antes de leerla. Los códigos muy chicos o muy borrosos no se leen. |
| La barra no aparece | Fijate que el ícono esté en la bandeja. Si no está, la app no se está ejecutando: corré `run.bat`. |
| Quiero ver los errores | Ejecutá `.venv\Scripts\python ejecutar.py` desde una consola en la carpeta del proyecto: ahí se ven los mensajes (`run.bat` usa `pythonw.exe`, que los esconde). |
| Doble click en `run.bat` y "no pasa nada" | Si la app ya estaba corriendo, la segunda copia se cierra sola para no dejar dos íconos en la bandeja. Usá el ícono que ya está. |
