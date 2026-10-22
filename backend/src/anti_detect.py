from typing import Dict, List

DEFAULT_CHROME_VERSION = "124"
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


def get_default_headers(user_agent: str = DEFAULT_USER_AGENT) -> Dict[str, str]:
    """Retorna cabeceras realistas de navegador que coinciden con las firmas de Chrome."""
    return {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Referer": "https://www.tiktok.com/",
        "sec-ch-ua": f'"Chromium";v="{DEFAULT_CHROME_VERSION}", "Google Chrome";v="{DEFAULT_CHROME_VERSION}", "Not-A.Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1"
    }


def get_stealth_browser_args() -> List[str]:
    """Argumentos de Chromium para deshabilitar banderas de automatización controlada."""
    return [
        "--disable-blink-features=AutomationControlled",
        "--disable-infobars",
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--window-size=1920,1080",
    ]


def get_stealth_init_script() -> str:
    """Script inyectado al inicio de la navegación para enmascarar navigator.webdriver."""
    return """
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        window.chrome = {
            runtime: {},
            app: {},
            csi: () => {},
            loadTimes: () => {}
        };
    """
