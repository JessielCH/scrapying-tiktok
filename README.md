# Plataforma de análisis de audiencias de TikTok

Monorepo con un backend Python para recopilar métricas públicas de perfiles y publicaciones de TikTok y analizarlas, y un dashboard React para consultar los resultados. El análisis incluye estimaciones lingüísticas de edad, rasgos Big Five, emociones, métricas de calidad de audiencia (AQS) y una síntesis de riesgo.

> Las estimaciones psicométricas y demográficas son inferencias estadísticas sobre comentarios, no datos verificados de las personas que los publicaron. No deben usarse para tomar decisiones individuales, médicas, legales o de elegibilidad. El uso de esta herramienta debe respetar los términos de TikTok y la normativa aplicable.

## Funcionalidades

- Auditoría de perfiles y análisis de hasta 30 publicaciones recientes, con comentarios asociados por video.
- Análisis agregado y por publicación: distribución de edad estimada, rasgos Big Five, emoción dominante y métricas AQS.
- Seguimiento del progreso de extracción y visualización de perfil, videos, comentarios y resultados en el dashboard.
- Captura opcional de evidencia multimedia local con manifiesto y hash SHA-256 para comprobar integridad del archivo.
- Síntesis ejecutiva con Google Gemini cuando hay una clave configurada; si no está disponible, se usa la evaluación determinista de respaldo.
- Clasificador local de Transformers desactivado por defecto. Se puede habilitar con `USE_LOCAL_TRANSFORMERS=true`.
- Flujo opcional de inicio de sesión QR para guardar cookies de sesión localmente.

## Estructura

```text
backend/
  api/                 # API FastAPI y esquemas Pydantic
  src/                 # Scraping, NLP, privacidad, cookies y evidencia
  data/
    evidence/          # Evidencias locales, ignoradas por Git
    reports/            # Informes locales, ignorados por Git
  main.py              # CLI interactiva, auditoría y servidor
  requirements.txt
frontend/
  src/
    components/        # Dashboard y componentes de resultados
    App.jsx
    index.css
  package.json
  vite.config.js        # Vite en el puerto 3000 y proxy /api al backend
```

## Requisitos

- Python 3.10 o superior.
- Node.js 18 o superior y npm.
- Chromium instalado para Playwright.
- Una clave `GEMINI_API_KEY` es opcional. Sin ella, el backend genera una síntesis de respaldo.

## Instalación y ejecución

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate       # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
cp .env.example .env            # Opcional; edita GEMINI_API_KEY si usarás Gemini
```

Inicia la API desde `backend/`:

```bash
python main.py server --host 127.0.0.1 --port 8000
```

La documentación interactiva queda en <http://127.0.0.1:8000/docs> y el estado del servicio en <http://127.0.0.1:8000/api/v1/health>.

También están disponibles la CLI interactiva (`python main.py`) y la auditoría directa:

```bash
python main.py audit "https://www.tiktok.com/@usuario/video/1234567890" --sample 150 --no-evidence
```

### Frontend

En otra terminal:

```bash
cd frontend
npm install
npm run dev
```

Abre <http://localhost:3000>. Vite reenvía las peticiones `/api` a `http://127.0.0.1:8000`. Si el backend no está disponible, el dashboard conserva su conjunto de datos de demostración.

## API

| Método | Ruta | Descripción |
| --- | --- | --- |
| `GET` | `/api/v1/health` | Estado del servicio y disponibilidad de cookies. |
| `POST` | `/api/v1/session/login-qr` | Inicia el flujo interactivo de login QR (hasta 5 minutos). |
| `GET` | `/api/v1/audit/progress` | Progreso y registros de la extracción en curso. |
| `POST` | `/api/v1/audit` | Analiza un perfil o URL de TikTok. |
| `GET` | `/api/v1/evidence/{filename}` | Descarga un archivo de evidencia guardado localmente. |

Ejemplo de solicitud a `/api/v1/audit`:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/audit \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://www.tiktok.com/@usuario",
    "sample_comments": 150,
    "max_videos": 10,
    "download_evidence": true,
    "headed_browser": false
  }'
```

`sample_comments` acepta valores de 10 a 1000 (por defecto, 150); `max_videos`, de 1 a 30 (por defecto, 10). `headed_browser` abre un navegador visible para resolver interacciones como captchas. La respuesta incluye metadatos del perfil, métricas agregadas, resultados por video, comentarios categorizados y una evaluación de riesgo.

## Configuración

Las variables reconocidas se documentan en [`backend/.env.example`](backend/.env.example):

- `GEMINI_API_KEY`: habilita la síntesis remota con Gemini; sin clave se usa el respaldo determinista.
- `DP_EPSILON`: epsilon de privacidad diferencial (por defecto, `1.0`).
- `DATA_DIR`: ubicación de cookies, evidencias e informes (por defecto, `backend/data`).
- `USE_LOCAL_TRANSFORMERS`: activa la carga local del clasificador cuando vale `true` o `1`.

## Privacidad y seguridad

- Las cookies y los datos locales de `backend/data/` están excluidos de Git. No publiques cookies, claves, evidencias ni informes.
- El extractor genera un hash SHA-256 de identificadores, pero los objetos de comentario también pueden contener nombre de usuario, nickname, avatar y texto. El hash es seudonimización; no implica que la respuesta esté anonimizada.
- El hash del manifiesto ayuda a comprobar la integridad del archivo capturado, pero no convierte el almacenamiento local en una bóveda inmutable ni certifica por sí solo cumplimiento legal.
- La API no implementa autenticación y configura CORS para cualquier origen. Su configuración predeterminada es para desarrollo local: no la expongas a Internet sin añadir controles de acceso y revisar CORS.

## Licencia

Distribuido bajo la [Licencia MIT](LICENSE).