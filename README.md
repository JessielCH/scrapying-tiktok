# Plataforma de Extracción y Análisis de Audiencias de TikTok

Plataforma integral basada en un backend en Python y un frontend en React (Vite) para extraer métricas públicas, publicaciones y comentarios reales de TikTok, analizando la composición demográfica por edades, rasgos psicométricos Big Five, emociones y calidad de interacción (AQS).

> **Aviso:** Las estimaciones psicométricas y demográficas son inferencias estadísticas basadas en modelos de procesamiento del lenguaje natural (NLP) sobre el texto de los comentarios públicos. No constituyen diagnósticos individuales ni datos personales sensibles de los usuarios.

---

## 🚀 Guía Rápida de Uso

### 1. Requisitos Previos
* **Python 3.10+**
* **Node.js 18+** y **npm**
* Navegador **Chromium** gestionado por Playwright

---

### 2. Puesta en Marcha del Backend

Abre una terminal en la raíz del proyecto y entra en la carpeta `backend`:

```powershell
# En Windows (PowerShell):
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
```

> **Nota para PowerShell:** Si la ejecución de scripts está restringida en Windows, ejecuta una sola vez:  
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

Inicia el servidor API:

```powershell
python main.py server
```

* **API REST disponible en:** `http://127.0.0.1:8000`
* **Documentación interactiva Swagger:** `http://127.0.0.1:8000/docs`
* **Comprobación de estado:** `http://127.0.0.1:8000/api/v1/health`

---

### 3. Puesta en Marcha del Frontend

Abre **otra ventana de terminal** y entra en la carpeta `frontend`:

```powershell
cd frontend
npm install
npm run dev
```

* **Dashboard Web accesible en:** `http://localhost:3000`

---

### 4. Cómo Usar la Interfaz Web

1. **Ingresar Objetivo:** Escribe el nombre de usuario de TikTok (por ejemplo: `@arigameplays` o `https://www.tiktok.com/@arigameplays`).
2. **Seleccionar Muestra de Videos:** Selecciona la cantidad de publicaciones recientes a extraer (1 a 30 videos).
3. **Muestra de Comentarios:** Define la cantidad de comentarios a capturar por video (ej. 150 comentarios).
4. **Modo Visual (Navegador visible):** Si TikTok solicita resolver un desafío o puzle deslizador, mantén marcado el modo visual para resolverlo en la ventana que se despliega (el sistema otorga hasta 5 minutos de espera automática con detección inteligente).
5. **Iniciar Extracción:** Haz clic en **"Extraer y Analizar"**. El sistema mostrará la barra de telemetría en tiempo real indicando el avance por video y comentarios.
6. **Explorar Resultados:**
   * **Métricas Globales Agregadas:** Resumen del total de comentarios, riesgo y calidad (AQS).
   * **Distribución de Edad Real Estimada:** Gráfico de anillo donde todos los porcentajes suman exactamente **100%**.
   * **Perfil Big Five:** Desglose porcentual normalizado de rasgos (Apertura, Responsabilidad, Dominancia Social, Estabilidad Emocional y Amabilidad), cuya suma matemática es **100%**.
   * **Desglose por Video:** Reproductor interactivo, visualización de métricas reales (visitas, likes, comentarios, compartidos) y lista desplegable con los comentarios reales capturados.

---

## 🧠 Funcionamiento Técnico y Evasión Anti-Bot

### Navegación Humana por Miniaturas (SPA)
A diferencia de los scripts tradicionales que fuerzan navegaciones directas mediante `page.goto(url_video)` (lo cual levanta bloqueos 403 inmediatos en Akamai Bot Manager), este sistema replica el flujo de un usuario real:
1. Navega fluidamente al perfil del creador.
2. Realiza desplazamientos aleatorios en la cuadrícula de publicaciones.
3. **Hace clic nativo sobre las miniaturas de video**, activando el modal interno de TikTok (SPA React) sin alterar el handshake TLS.
4. Extrae los comentarios cargados mediante la API interna `/api/comment/list/` y el DOM.
5. Cierra el modal pulsando la tecla `Escape` y pasa al siguiente video.

### Distribuciones Porcentuales Normalizadas (Suma 100%)
Todas las métricas de distribución en el sistema (edad estimada, autenticidad AQS y rasgos de personalidad Big Five) aplican normalización estocástica y balanceo de residuos para asegurar que **la suma total de las franjas siempre sea exactamente 100%** (o 0% en ausencia de datos), evitando inconsistencias de escalas independientes.

---

## 📁 Estructura del Proyecto

```text
scrap-tiktok/
├── backend/
│   ├── api/                 # Endpoints FastAPI y esquemas Pydantic
│   ├── src/                 # Lógica de scraping Playwright, NLP y privacidad
│   │   ├── comment_scraper.py # Extractor humano con clic modal SPA
│   │   ├── nlp_engine.py      # Motor psicolingüístico y clasificación Big Five
│   │   ├── privacy_dp.py      # Privacidad Diferencial (ε-DP) y métricas AQS
│   │   └── cookie_manager.py  # Manejo de cookies de sesión y login QR
│   ├── data/                # Almacenamiento local de cookies y descargas
│   ├── main.py              # CLI de consola y arranque del servidor
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # Componentes UI (gráficos, tarjetas de video, telemetría)
│   │   ├── App.jsx          # Vista principal del dashboard
│   │   └── index.css        # Estilos y diseño visual
│   ├── package.json
│   └── vite.config.js       # Servidor Vite en puerto 3000 con proxy a :8000
└── README.md
```

---

## 🔒 Privacidad y Configuración

El archivo `backend/.env` permite configurar parámetros adicionales (opcional):

```env
GEMINI_API_KEY=tu_clave_de_gemini_opcional
DP_EPSILON=1.0
DATA_DIR=data
```

* Si no se especifica `GEMINI_API_KEY`, el sistema genera una síntesis lingüística determinista de respaldo sin depender de APIs de pago.
* Las cookies y datos capturados permanecen en almacenamiento local y están estrictamente excluidos de Git por `.gitignore`.

---

## 📄 Licencia

Este proyecto está distribuido bajo la [Licencia MIT](LICENSE).