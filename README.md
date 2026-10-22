# Plataforma de Auditoría Demográfica, Psicometría y Evidencia Forense en Redes Sociales

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18.3.1-61dafb.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/vite-5.2-646cff.svg)](https://vitejs.dev/)
[![Playwright](https://img.shields.io/badge/playwright-stealth-green.svg)](https://playwright.dev/)
[![TLS Impersonation](https://img.shields.io/badge/TLS-curl__cffi-orange.svg)](https://github.com/yifeikong/curl_cffi)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688.svg)](https://fastapi.tiangolo.com/)
[![Gemini 1.5 Flash](https://img.shields.io/badge/AI-Gemini%201.5%20Flash-4285f4.svg)](https://ai.google.dev/)
[![Licencia: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Plataforma de ingeniería estructurada en **Monorepo** para la auditoría de audiencias, psicometría computacional (Big Five), estimación etaria real mediante Procesamiento de Lenguaje Natural (NLP), preservación de evidencia forense inmutable y evaluación de riesgos comerciales (Brand Safety) y parentales (estilo Bark).

---

## Características Principales

- **Arquitectura Monorepo:** Centraliza el motor analítico (`backend/`) y el panel de control ejecutivo (`frontend/`), compartiendo contratos de API y configuraciones de despliegue.
- **Bóveda de Evidencia Forense Inmutable:** Descarga automatizada de videos con `yt-dlp` y certificación de autenticidad pericial mediante **firmas SHA-256** y marcas de tiempo UTC.
- **Scraping Ético y Privacidad (LOPDP Ecuador Arts. 19 y 21):** Extracción de comentarios con **hashing unidireccional SHA-256 en memoria** para impedir cualquier exposición de identidades personales o de menores.
- **Psicometría y Modelado Big Five (NLP):**
  - Clasificación Zero-Shot con `mDeBERTa-v3` multilingüe adaptada a jerga hispana.
  - Estimación etaria probabilística basada en las trayectorias del desarrollo normativo (Roberts et al., 2006; Soto et al., 2011).
  - Detección de emociones básicas de Ekman con `pysentimiento` (RoBERTuito).
- **Garantías Matemáticas de Privacidad Diferencial ($\epsilon$-DP):** Inyección de ruido Laplaciano sobre las distribuciones agregadas de edad y personalidad.
- **Síntesis Ejecutiva con Gemini 1.5 Flash:** Generación de dictámenes estructurados en JSON sobre viabilidad comercial de pauta y alertas de control parental predictivo.
- **Dashboard Clínico Ejecutivo:** Interfaz aséptica en React 18 con fondos blancos puros, gráficos de anillos de edad en SVG, semáforos de riesgo y descarga pericial.

---

## Estructura del Monorepo

```text
scrap-tiktok/
├── backend/                              # Motor Computacional y APIs REST (Python 3.10+)
│   ├── api/                              # Servidor FastAPI y esquemas Pydantic
│   │   ├── __init__.py
│   │   ├── app.py                        # Endpoints REST (/audit, /evidence, /health)
│   │   └── schemas.py                    # Validación de contratos de datos
│   ├── src/                              # Módulos core de ingeniería
│   │   ├── __init__.py
│   │   ├── cookie_manager.py             # Sesiones Playwright (Guest y QR Login)
│   │   ├── anti_detect.py                # Camuflaje TLS JA3/JA4 y bypass de automatización
│   │   ├── comment_scraper.py            # Extracción y anonimización SHA-256 de comentarios
│   │   ├── forensic_vault.py             # Preservación de video inmutable y firma SHA-256
│   │   ├── nlp_engine.py                 # mDeBERTa-v3 Zero-Shot NLI y emociones de Ekman
│   │   ├── privacy_dp.py                 # Privacidad Diferencial (ε-DP) y métricas AQS
│   │   ├── gemini_synthesizer.py         # Cliente Gemini 1.5 Flash con salida JSON estricta
│   │   ├── scraper.py                    # Extracción SSR y streaming de video
│   │   ├── user_analyzer.py              # Analizador estadístico de perfiles y posts
│   │   └── utils.py                      # Serializadores Netscape y CSVs
│   ├── data/                             # Almacén local protegido (en .gitignore)
│   │   ├── evidence/                     # Videos MP4 forenses y manifiestos
│   │   └── reports/                      # Reportes CSV, JSON y dictámenes
│   ├── .env.example                      # Plantilla de variables de entorno
│   ├── requirements.txt                  # Dependencias de Python del backend
│   └── main.py                           # CLI interactivo y lanzador del servidor
├── frontend/                             # Dashboard Clínico Ejecutivo (React / Vite)
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx                # Barra superior y sellos de seguridad LOPDP
│   │   │   ├── AuditSearch.jsx           # Barra de búsqueda clínica para URLs
│   │   │   ├── EvidenceCard.jsx          # Clasificación y descarga pericial SHA-256
│   │   │   ├── AgeDonutChart.jsx         # Gráfico de anillos de edad real estimada
│   │   │   ├── BigFiveProfile.jsx        # Barras de Responsabilidad, Dominancia y Afecto
│   │   │   ├── RiskGauge.jsx             # Medidor visual de riesgo (Verde/Amarillo/Rojo)
│   │   │   └── ExecutiveSummary.jsx      # Conclusiones de Gemini en tercera persona
│   │   ├── App.jsx                       # Orquestación del estado del dashboard
│   │   ├── main.jsx
│   │   └── index.css                     # Sistema de diseño clínico (fondo blanco puro)
│   ├── package.json                      # Dependencias de React y bibliotecas UI
│   └── vite.config.js
├── .gitignore                            # Blindaje estricto contra fugas de credenciales
├── CONTRIBUTING.md                       # Protocolos de desarrollo
├── CODE_OF_CONDUCT.md                   # Código de conducta
├── LICENSE                               # Licencia MIT
├── README.md                             # Documentación principal (este archivo)
└── SECURITY.md                           # Políticas de reporte de vulnerabilidades
```

---

## Instalación y Puesta en Marcha

### 1. Requisitos Previos
- Python 3.10 o superior instalado.
- Node.js 18+ y npm instalados.
- Git instalado.

### 2. Configuración del Backend

```bash
cd backend

# Crear el entorno virtual aislado
python -m venv .venv

# Activar en Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Nota: Si PowerShell bloquea scripts, ejecuta antes: Set-ExecutionPolicy -Scope Process RemoteSigned

# Activar en Windows (Símbolo del sistema / CMD):
.venv\Scripts\activate.bat

# Activar en Linux / macOS:
# source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar navegadores para Playwright
playwright install chromium

# Configurar variables de entorno (opcional para Gemini)
copy .env.example .env
```

#### Modos de Ejecución del Backend:

- **Modo Servidor API REST (para alimentar al Dashboard):**
  ```bash
  python main.py server --port 8000
  ```
  *Documentación Swagger interactiva:* `http://localhost:8000/docs`

- **Modo Menú Interactivo en Consola:**
  ```bash
  python main.py
  ```

---

### 3. Configuración del Frontend (Dashboard Ejecutivo)

En una terminal separada:

```bash
cd frontend

# Instalar paquetes
npm install

# Iniciar servidor de desarrollo
npm run dev
```

El panel estará disponible de forma inmediata en:
👉 `http://localhost:3000`

---

## Blindaje de Seguridad y Privacidad (.gitignore)

El repositorio cuenta con una directiva estricta de **cero fugas de información sensible**:
- Las cookies de sesión (`*cookies.json`, `*cookies.txt`), las variables de entorno (`.env`), los videos `.mp4` descargados como evidencia y los reportes locales **están estrictamente ignorados por Git**.
- Las carpetas `backend/data/evidence/` y `backend/data/reports/` contienen únicamente archivos `.gitkeep` para garantizar que la estructura exista al clonar el repositorio sin exponer ningún archivo privado.

---

## Licencia

Distribuido bajo la [Licencia MIT](LICENSE).
