"""
Paquete de Auditoría Demográfica, Psicometría y Evidencia Forense
=================================================================
Proporciona la interfaz unificada de los módulos del Backend:
- Gestión de sesiones y anti-detección.
- Extracción ética y anonimización de comentarios (LOPDP).
- Bóveda de evidencia forense inmutable (yt-dlp + SHA-256).
- Psicometría computacional Big Five y estimación etaria con NLP.
- Privacidad diferencial y cálculo de AQS.
- Síntesis y evaluación de riesgos con Gemini 1.5 Flash.
"""

from .cookie_manager import TikTokCookieManager
from .scraper import TikTokScraper
from .user_analyzer import TikTokUserAnalyzer
from .comment_scraper import TikTokCommentScraper
from .forensic_vault import ForensicVault
from .privacy_dp import DifferentialPrivacyEngine, AudienceQualityAnalyzer
from .nlp_engine import PsychometricsNLPEngine
from .gemini_synthesizer import GeminiRiskSynthesizer
from .anti_detect import get_default_headers, get_stealth_browser_args

__all__ = [
    "TikTokCookieManager",
    "TikTokScraper",
    "TikTokUserAnalyzer",
    "TikTokCommentScraper",
    "ForensicVault",
    "DifferentialPrivacyEngine",
    "AudienceQualityAnalyzer",
    "PsychometricsNLPEngine",
    "GeminiRiskSynthesizer",
    "get_default_headers",
    "get_stealth_browser_args",
]

__version__ = "2.0.0"
__author__ = "JessielCH"
