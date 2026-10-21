import json
from pathlib import Path
from typing import Optional, Dict, Any
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    from curl_cffi import requests
except ImportError:
    requests = None

from .utils import load_cookies, ensure_output_dir
from .anti_detect import get_default_headers


class TikTokScraper:
    """
    High-performance TikTok scraper leveraging SSR hydration data
    and Chrome TLS impersonation via curl_cffi.
    """

    def __init__(self, cookies_path: Optional[str] = "data/cookies.json", impersonate: str = "chrome120"):
        self.impersonate = impersonate
        self.cookies: Dict[str, str] = {}
        if cookies_path:
            self.cookies = load_cookies(Path(cookies_path))

    def _check_dependencies(self):
        missing = []
        if requests is None:
            missing.append("curl_cffi")
        if BeautifulSoup is None:
            missing.append("beautifulsoup4")
        if missing:
            raise RuntimeError(
                f"Missing dependencies: {', '.join(missing)}. "
                f"Please run: pip install {' '.join(missing)}"
            )

    def get_metadata(self, url: str) -> Dict[str, Any]:
        """
        Fetches metadata for a video or user profile using the SSR hydration payload.
        """
        self._check_dependencies()
        headers = get_default_headers()

        print(f"[*] Consultando {url} con emulación de huella TLS ({self.impersonate})...")
        response = requests.get(
            url,
            impersonate=self.impersonate,
            headers=headers,
            cookies=self.cookies,
            timeout=30
        )

        if response.status_code != 200:
            raise RuntimeError(f"HTTP {response.status_code}: Error al cargar la página de TikTok")

        soup = BeautifulSoup(response.text, "html.parser")

        # 1. Check for primary SSR tag: __UNIVERSAL_DATA_FOR_REHYDRATION__
        tag = soup.find("script", id="__UNIVERSAL_DATA_FOR_REHYDRATION__")
        if tag and tag.string:
            raw = json.loads(tag.string)
            scope = raw.get("__DEFAULT_SCOPE__", {})

            # Video or Carousel item struct
            video_detail = scope.get("webapp.video-detail", {})
            item = video_detail.get("itemInfo", {}).get("itemStruct")
            if item:
                # Check for carousel
                image_post = item.get("imagePostInfo") or item.get("imagePost") or {}
                images_raw = image_post.get("images") or []
                if not images_raw and "images" in item and isinstance(item["images"], list):
                    images_raw = item["images"]

                if images_raw:
                    image_urls = []
                    for img in images_raw:
                        if isinstance(img, dict):
                            img_data = img.get("imageURL") or img.get("displayImage") or img.get("thumbnail") or img
                            if isinstance(img_data, dict):
                                urls = img_data.get("urlList") or img_data.get("url_list") or []
                                if urls:
                                    image_urls.append(urls[0])
                            elif isinstance(img_data, str):
                                image_urls.append(img_data)
                        elif isinstance(img, str):
                            image_urls.append(img)
                    return {"type": "carousel", "data": item, "images": image_urls}

                return {"type": "video", "data": item}

            # User profile info
            user_detail = scope.get("webapp.user-detail", {})
            user_info = user_detail.get("userInfo")
            if user_info:
                return {"type": "user", "data": user_info}

        # 2. Check for legacy/alternative SIGI_STATE tag
        sigi = soup.find("script", id="SIGI_STATE")
        if sigi and sigi.string:
            raw = json.loads(sigi.string)
            item_module = raw.get("ItemModule", {})
            if item_module:
                first_key = next(iter(item_module))
                return {"type": "video", "data": item_module[first_key]}

        raise ValueError(
            "No se pudo localizar la etiqueta de hidratación SSR de TikTok en el HTML. "
            "Es posible que TikTok haya presentado un captcha de verificación o que la URL sea inválida."
        )

    def download_carousel_images(self, image_urls: List[str], output_dir: str) -> List[Path]:
        """
        Descarga todas las fotos de un carrusel de diapositivas de TikTok.
        """
        self._check_dependencies()
        folder = Path(output_dir)
        ensure_output_dir(folder)

        saved_files = []
        headers = {
            "User-Agent": get_default_headers()["User-Agent"],
            "Referer": "https://www.tiktok.com/",
        }

        print(f"[*] Descargando {len(image_urls)} diapositivas del carrusel en {folder}...")
        for i, url in enumerate(image_urls, 1):
            out_path = folder / f"slide_{i}.jpg"
            try:
                res = requests.get(
                    url,
                    impersonate=self.impersonate,
                    headers=headers,
                    cookies=self.cookies,
                    timeout=20
                )
                if res.status_code == 200:
                    with open(out_path, "wb") as f:
                        f.write(res.content)
                    saved_files.append(out_path)
            except Exception as e:
                print(f"[!] Aviso al descargar la diapositiva #{i}: {e}")

        print(f"[OK] Descarga del carrusel completada: {len(saved_files)}/{len(image_urls)} fotos guardadas.")
        return saved_files

    def download_video(self, video_url: str, output_path: str) -> Path:
        """
        Descarga un video sin marca de agua directamente desde la URL CDN del stream.
        """
        self._check_dependencies()
        output_file = Path(output_path)
        ensure_output_dir(output_file.parent)

        headers = {
            "User-Agent": get_default_headers()["User-Agent"],
            "Referer": "https://www.tiktok.com/",
            "Range": "bytes=0-"
        }

        print(f"[*] Transmitiendo y guardando video en {output_file}...")
        res = requests.get(
            video_url,
            impersonate=self.impersonate,
            headers=headers,
            cookies=self.cookies,
            stream=True
        )

        if res.status_code not in [200, 206]:
            raise RuntimeError(f"HTTP {res.status_code}: Error al descargar el flujo de video")

        with open(output_file, "wb") as f:
            for chunk in res.iter_content(chunk_size=1024 * 64):
                if chunk:
                    f.write(chunk)

        print(f"[OK] Descarga completada exitosamente: {output_file}")
        return output_file
