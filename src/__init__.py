"""
Paquete interno de módulos locales de scraping.
=================================================
Aclaración: Los siguientes módulos no corresponden a librerías externas
ni a paquetes prefabricados de terceros. Son clases y funciones desarrolladas
localmente desde cero dentro de este repositorio (en los archivos .py de la carpeta src/).

Módulos locales:
- .cookie_manager -> src/cookie_manager.py (Gestión local de cookies con Playwright)
- .scraper        -> src/scraper.py (Extracción de HTML/SSR con BeautifulSoup)
- .user_analyzer  -> src/user_analyzer.py (Analizador numérico de perfil y publicaciones)
- .anti_detect    -> src/anti_detect.py (Cabeceras y scripts de evasión)
- .utils          -> src/utils.py (Utilidades y serialización Netscape/JSON)
"""

from .cookie_manager import TikTokCookieManager
from .scraper import TikTokScraper
from .user_analyzer import TikTokUserAnalyzer
from .anti_detect import get_default_headers, get_stealth_browser_args

__all__ = [
    "TikTokCookieManager",
    "TikTokScraper",
    "TikTokUserAnalyzer",
    "get_default_headers",
    "get_stealth_browser_args",
]

__version__ = "1.0.0"
