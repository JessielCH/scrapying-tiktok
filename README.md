# TikTok Scraper & Gestor de Cookies de Sesión

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/playwright-stealth-green.svg)](https://playwright.dev/)
[![TLS Impersonation](https://img.shields.io/badge/TLS-curl__cffi-orange.svg)](https://github.com/yifeikong/curl_cffi)
[![Cero APIs Externas](https://img.shields.io/badge/APIs%20Externas-Ninguna%20(Scraping%20Puro)-success.svg)](#)
[![Sin Wrappers de Terceros](https://img.shields.io/badge/Librer%C3%ADas%20TikTok-Ninguna%20(Nativo%20Directo)-blueviolet.svg)](#)
[![Licencia: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Un conjunto de herramientas de alto rendimiento, sigiloso y modular para la extracción de datos (web scraping) y gestión de sesiones en **TikTok**. Diseñado para sortear las protecciones de Akamai Bot Manager, huellas digitales TLS (JA3/JA4) y barreras de firmas criptográficas dinámicas, con soporte integral para sesiones de invitado y cuentas autenticadas.

---

## Características Principales

- **Scraping Web Puro (Cero APIs Externas, Cero Wrappers Prediseñados):** Totalmente autónomo. No requiere APIs de desarrolladores de TikTok, ni tokens de pago (Apify, RapidAPI), ni librerías wrapper de terceros (como `TikTokApi` o `pyktok`).
- **Anti-Detección y Evasión TLS:** Utiliza `curl_cffi` para replicar con exactitud el apretón de manos TLS de Chrome 120/124 (huellas JA3/JA4), evitando respuestas directas de bloqueo `HTTP 403 Forbidden`.
- **Gestión Completa de Sesiones y Cookies:**
  - **Modo Invitado (`--mode guest`):** Extracción automatizada en segundo plano (headless) de cookies públicas indispensables (`ttwid`, `msToken`).
  - **Modo Inicio de Sesión Interactivo (`--mode login`):** Abre un navegador Chromium visible para iniciar sesión manual o mediante código QR, capturando sesiones autenticadas completas (`sessionid`, `sessionid_ss`).
  - **Exportación Dual:** Guarda el estado en JSON (formato de almacenamiento de Playwright) y en formato estándar Netscape (`cookies.txt` compatible con `yt-dlp` y `curl`).
- **Soporte para Videos y Carruseles de Fotos (Slideshows):** Detecta automáticamente si una publicación es un video o un carrusel de diapositivas, extrayendo el número de fotos, enlaces a las imágenes o flujo de video, y todas las métricas numéricas.
- **Extracción Rápida por Hidratación SSR:** Obtiene la información directamente de la etiqueta `<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__">` inyectada por el servidor, eliminando la necesidad de ejecutar JavaScript pesado o firmar tokens `X-Bogus`.
- **Descarga de Medios Sin Marca de Agua:** Descarga directa de transmisiones de video en alta calidad (`playAddr` / `downloadAddr`) y descarga por lotes de todas las imágenes de carruseles.
- **Consola Interactiva:** Interfaz estructurada por terminal para ingresar perfiles, elegir cantidad de posts a analizar y alternar opciones visuales.

---

## Filosofía de Diseño: Cero APIs y Cero Wrappers de Terceros

Un principio fundamental de este proyecto es la **ingeniería directa, básica y transparente**:
- **Sin APIs Oficiales:** No se requiere solicitar acceso al portal de desarrolladores de TikTok, ni registrar aplicaciones OAuth, ni gestionar claves secretas o límites de cuota.
- **Sin Librerías Wrapper de Python:** No se depende de paquetes externos como `TikTokApi` o `pyktok`, los cuales quedan obsoletos frecuentemente cada vez que TikTok actualiza sus endpoints internos.
- **Sin Servicios de Scraping de Pago:** Funciona sin suscripciones a plataformas como Apify, ScraperAPI, RapidAPI o BrightData.
- **Mecanismos Web Nativos:**
  1. Inspección directa del DOM y renderizado real mediante **Playwright**.
  2. Parseo directo del HTML y del estado del servidor (`__UNIVERSAL_DATA_FOR_REHYDRATION__`) mediante **BeautifulSoup**.
  3. Peticiones HTTP estándar con paridad de huella TLS mediante **curl_cffi**.

---

## Estructura del Repositorio

```text
scrap-tiktok/
├── src/                                                # Paquete fuente principal
│   ├── __init__.py                                     # Exportación de clases y módulos
│   ├── cookie_manager.py                               # Gestor de cookies y sesiones con Playwright
│   ├── scraper.py                                      # Scraper SSR y descargas directas de medios
│   ├── user_analyzer.py                                # Analizador numérico de perfiles y publicaciones
│   ├── anti_detect.py                                  # Cabeceras realistas y scripts de evasión
│   └── utils.py                                        # Serializadores Netscape/JSON y utilidades
├── data/                                               # Almacén de sesiones y descargas (en .gitignore)
│   ├── .gitkeep
│   └── downloads/
│       └── .gitkeep
├── main.py                                             # Punto de entrada unificado y menú interactivo
├── requirements.txt                                    # Dependencias de Python
├── CONTRIBUTING.md                                     # Guía para colaboradores
├── CODE_OF_CONDUCT.md                                 # Código de conducta
├── LICENSE                                             # Licencia MIT
├── README.md                                           # Documentación del proyecto (este archivo)
└── SECURITY.md                                         # Política de seguridad
```

---

## Instalación y Puesta en Marcha

### 1. Requisitos Previos
- Python 3.10 o superior instalado.
- Git instalado.

### 2. Instalación Paso a Paso

Clona el repositorio e instala las dependencias necesarias:

```bash
git clone https://github.com/JessielCH/scrapying-tiktok.git
cd scrapying-tiktok

# Crear y activar el entorno virtual
python -m venv .venv

# En Windows (PowerShell / CMD):
.venv\Scripts\activate
# En Linux / macOS:
# source .venv/bin/activate

# Instalar dependencias requeridas
pip install -r requirements.txt

# Instalar el navegador Chromium de Playwright
playwright install chromium
```

---

## Guía de Uso

### Modo Interactivo por Consola (Recomendado)
Para iniciar la experiencia interactiva, ejecuta `main.py` sin argumentos:

```bash
python main.py
```

El menú te permitirá de forma guiada:
1. **Analizar Perfil y Publicaciones (CSV / DataFrame):** Ingresar cualquier usuario (`@usuario`), extraer su perfil y últimos posts con métricas numéricas, y exportar los datos automáticamente a `data/posts_<usuario>.csv` y `data/analysis_<usuario>.json`.
2. **Extraer / Renovar Cookies de Sesión:** Escoger entre el modo Invitado rápido o el inicio de sesión con código QR en Chromium para asegurar acceso permanente y evitar bloqueos.
3. **Salir:** Finalizar la sesión.

---

### 1. Extracción y Gestión de Cookies

TikTok requiere cookies válidas (en especial `ttwid`) para procesar consultas sin arrojar pantallas de bloqueo.

#### A. Modo Invitado (Automático, Sin Ventana)
Extrae las cookies públicas necesarias de forma desatendida:
```bash
python main.py extract-cookies --mode guest
```
Archivos generados en la carpeta `data/`:
- `data/cookies.json` (formato compatible con Playwright)
- `data/cookies.txt` (formato estándar Netscape para `yt-dlp` y `curl`)

#### B. Modo Autenticado con Inicio de Sesión (Interactivo)
Abre una ventana de navegador real para iniciar sesión con credenciales o escaneando el código QR:
```bash
python main.py extract-cookies --mode login
```
*Al detectar el inicio de sesión exitoso, el sistema guarda de inmediato `sessionid` y todas las cookies del usuario.*

---

### 2. Análisis Numérico de Perfil y Últimos Posts (Videos y Carruseles)

Extrae el perfil completo de un usuario de TikTok:
- Nombre de usuario y nombre visible (apodo).
- Biografía.
- Estado de verificación (cuenta verificada o no).
- Contador de seguidos y seguidores.
- Total de likes recibidos y total de videos publicados.

Y analiza **numéricamente** sus últimos posts (tanto videos tradicionales como carruseles de fotos):
- Total de likes, comentarios, guardados (favoritos), compartidos y reproducciones/vistas.
- Promedios por publicación (promedio de likes, comentarios, guardados, compartidos y vistas).
- Tasa de interacción (Engagement Rate) calculada en base a visualizaciones.
- Desglose detallado de cada publicación con su tipo (Video o Carrusel con número de diapositivas).

#### Comandos Directos por Terminal:

```bash
# Analizar usuario con los últimos 10 posts por defecto
python main.py analyze-user @usuario

# Analizar con un número personalizado de posts
python main.py analyze-user @usuario --max-videos 15

# Usar cookies de sesión previamente guardadas
python main.py analyze-user @usuario --cookies data/cookies.json

# Ejecutar con navegador visible (útil si TikTok muestra el captcha de deslizar el rompecabezas)
python main.py analyze-user @usuario --headed
```

El reporte se imprime ordenadamente en la consola y se exporta de forma automática en dos formatos complementarios en la carpeta `data/`:
1. **`data/posts_<usuario>.csv`:** Archivo tabular con el desglose de cada publicación (ID, tipo, descripción, likes, comentarios, guardados, compartidos, vistas, fotos y fecha). Ideal para abrir en Microsoft Excel o cargarlo de inmediato en Python como un **DataFrame de pandas**.
2. **`data/analysis_<usuario>.json`:** Estructura jerárquica con los metadatos completos del perfil, estadísticas globales, promedios y tasas de interacción.

---

### 3. Scraping y Descarga de Publicaciones Individuales

Permite obtener los metadatos de un video o carrusel puntual y descargar el archivo multimedia sin marcas de agua:

```bash
# Solo ver los metadatos y enlaces
python main.py scrape "https://www.tiktok.com/@usuario/video/1234567890123456789"

# Descargar automáticamente el video en MP4 o las diapositivas del carrusel en JPG
python main.py scrape "https://www.tiktok.com/@usuario/video/1234567890123456789" --download
```

---

### 4. Uso como Módulo de Python

Puedes importar y reutilizar las clases directamente en tus propios scripts o proyectos de Python:

```python
import pandas as pd
from src.user_analyzer import TikTokUserAnalyzer

# 1. Extraer datos numéricos de perfil y publicaciones
analyzer = TikTokUserAnalyzer()
reporte = analyzer.analyze_user("mrbeast", max_videos=10)

# 2. Cargar directamente el CSV generado en un DataFrame de pandas
df = pd.read_csv("data/posts_mrbeast.csv")

# 3. Análisis descriptivo de los datos
print("Primeras filas del DataFrame:")
print(df[["tipo", "likes", "comentarios", "guardados", "vistas"]].head())

print("\nResumen estadístico:")
print(df[["likes", "comentarios", "guardados", "vistas"]].describe())
```

---

### 5. Descarga Alternativa con `yt-dlp`

Puedes aprovechar el archivo de cookies en formato Netscape (`data/cookies.txt`) generado por este proyecto para descargar videos con `yt-dlp`:

```bash
yt-dlp --cookies data/cookies.txt "https://www.tiktok.com/@usuario/video/1234567890123456789" -o "data/downloads/%(id)s.%(ext)s"
```

---

## Detalles de Evasión y Anti-Detección

El sistema Akamai Bot Manager de TikTok inspecciona el paquete inicial de conexión `ClientHello` de TLS. Las librerías convencionales como `requests` o `urllib` generan firmas anómalas que son bloqueadas al instante.

| Factor | Scraping Convencional | Este Proyecto |
| :--- | :--- | :--- |
| **Apretón de Manos TLS (JA3/JA4)** | Predeterminado de Python (Bloqueo 403) | Simulación exacta de Chrome 120+ mediante `curl_cffi` |
| **Contexto del Navegador** | `navigator.webdriver = true` | Evasión y camuflaje mediante scripts stealth en `playwright` |
| **Rastreo de Sesión** | Ausencia de `ttwid` (Error 10202) | Gestión automatizada de cookies de invitado y autenticadas |
| **Extracción de Datos** | Llamadas complejas con tokens `X-Bogus` | Hidratación del servidor SSR (`__UNIVERSAL_DATA_FOR_REHYDRATION__`) |

---

## Contribuciones

Las contribuciones son bienvenidas. Revisa [CONTRIBUTING.md](CONTRIBUTING.md) y el [Código de Conducta](CODE_OF_CONDUCT.md) antes de enviar propuestas o mejoras.

---

## Aviso Legal

Este proyecto ha sido desarrollado exclusivamente con fines educativos, de investigación académica y archivo de datos. La recolección de información debe cumplir con los términos de servicio de la plataforma y las normativas legales pertinentes sobre derechos de autor y privacidad. El autor no asume responsabilidad alguna por el uso indebido de esta herramienta.

---

## Licencia

Distribuido bajo la [Licencia MIT](LICENSE).
