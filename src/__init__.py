"""
Paquete de Extracción y Análisis de Datos para TikTok
======================================================
Proporciona la interfaz unificada del paquete exponiendo los componentes
principales para la gestión de sesiones, navegación automatizada, análisis
estadístico de perfiles y extracción de contenido multimedia.
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
__author__ = "JessielCH"
