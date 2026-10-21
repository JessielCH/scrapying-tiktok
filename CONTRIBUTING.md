# Guía de Contribución para TikTok Scraper & Gestor de Cookies

En primer lugar, ¡muchas gracias por tu interés en contribuir a este proyecto! La colaboración hace que el software libre y las herramientas abiertas crezcan.

---

## Código de Conducta

Al participar en este repositorio, aceptas adherirte a nuestro [Código de Conducta](CODE_OF_CONDUCT.md). Por favor informa cualquier comportamiento inapropiado al mantenedor del proyecto.

---

## ¿Cómo Puedo Contribuir?

### Reportar Errores (Bugs)
Antes de crear un nuevo reporte de error, revisa los issues existentes para evitar duplicados. Al reportar un problema, incluye:
- Un título claro y descriptivo.
- Pasos ordenados para reproducir el fallo.
- Códigos de error o respuestas de TikTok (ej. HTTP 403, 10202, bloqueo por captcha).
- Sistema operativo y versión de Python utilizada.
- **No incluyas cookies personales ni credenciales privadas en los reportes o capturas.**

### Sugerir Mejoras y Nuevas Características
¡Las propuestas son bienvenidas! Al sugerir una funcionalidad, describe:
- El problema o caso de uso que deseas resolver.
- Tu propuesta de solución o diseño del código.
- Cualquier información relevante sobre la estructura de TikTok.

### Pull Requests
1. Realiza un **Fork** del repositorio y crea tu rama desde `main`:
   ```bash
   git checkout -b feature/nombre-de-tu-mejora
   ```
2. Instala las dependencias y prueba tus cambios en un entorno virtual aislado.
3. Respeta los estándares del proyecto:
   - Seguir las pautas de estilo **PEP 8**.
   - Incluir anotaciones de tipo (*type hints*) en funciones principales.
   - Documentar funciones de forma clara.
4. Realiza commits con mensajes descriptivos siguiendo el estándar [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat: agregar soporte para extracción de comentarios`
   - `fix: manejar expiración de cookie ttwid correctamente`
   - `docs: actualizar guía de uso en el README`
5. Sube tu rama y abre un **Pull Request** hacia `main`.

---

## Configuración del Entorno de Desarrollo

```bash
git clone https://github.com/JessielCH/scrapying-tiktok.git
cd scrapying-tiktok
python -m venv .venv

# En Windows:
.venv\Scripts\activate
# En Linux / macOS:
# source .venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

---

## Pautas de Seguridad y Privacidad

- Nunca subas al repositorio cookies reales de usuarios (`sessionid`), tokens o contraseñas.
- Los archivos en la carpeta `data/` están ignorados por `.gitignore` para proteger tu privacidad.
