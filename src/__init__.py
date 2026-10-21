"""
TikTok Scraper & Session Cookie Manager Package.
"""

from .cookie_manager import TikTokCookieManager
from .scraper import TikTokScraper
from .anti_detect import get_default_headers, get_stealth_browser_args

__all__ = [
    "TikTokCookieManager",
    "TikTokScraper",
    "get_default_headers",
    "get_stealth_browser_args",
]

__version__ = "1.0.0"
