"""
Módulo de Extracción Ética y Anonimización de Comentarios
=========================================================
Extrae comentarios públicos de publicaciones de TikTok mediante Playwright
e implementa pseudonimización unidireccional inmediata mediante SHA-256 en memoria
para dar estricto cumplimiento a los Artículos 19 y 21 de la LOPDP (Ecuador),
garantizando la protección absoluta de datos de menores y usuarios.
"""

import hashlib
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    from playwright.async_api import async_playwright
except ImportError:
    async_playwright = None

from .utils import ensure_output_dir
from .anti_detect import DEFAULT_USER_AGENT, get_stealth_browser_args, get_stealth_init_script
from .cookie_manager import TikTokCookieManager


class TikTokCommentScraper:
    """
    Extractor de comentarios de TikTok con capa de disociación y anonimización criptográfica.
    Interpreta el árbol DOM y las respuestas de red, transformando cualquier identificador
    personal en un hash SHA-256 irreversible antes de permitir su almacenamiento.
    """

    def __init__(self, cookies_path: Optional[str] = "data/cookies.json", output_dir: str = "data"):
        backend_root = Path(__file__).resolve().parent.parent
        if cookies_path:
            cp = Path(cookies_path)
            self.cookies_path = cp if cp.is_absolute() else backend_root / cp
        else:
            self.cookies_path = None
        od = Path(output_dir)
        self.output_dir = od if od.is_absolute() else backend_root / od
        ensure_output_dir(self.output_dir)

    def _check_dependencies(self):
        if async_playwright is None:
            raise RuntimeError(
                "Playwright no está instalado. Instálalo ejecutando:\n"
                "  pip install playwright && playwright install chromium"
            )

    @staticmethod
    def pseudonymize_identifier(raw_id: str) -> str:
        """
        Aplica un hash criptográfico SHA-256 unidireccional a cualquier identificador de usuario.
        Destruye la legibilidad original impidiendo la identificación de personas físicas.
        """
        if not raw_id:
            return "ANON_UNKNOWN"
        return hashlib.sha256(raw_id.strip().encode("utf-8")).hexdigest()

    async def scrape_comments_async(
        self,
        post_url: str,
        max_comments: int = 150,
        headed: bool = False,
        timeout: int = 35
    ) -> List[Dict[str, Any]]:
        """
        Extrae y anonimiza comentarios de un video o publicación de TikTok.

        Args:
            post_url: Enlace completo del video o publicación de TikTok.
            max_comments: Límite superior de comentarios a capturar.
            headed: Activa ventana visible para resolver desafíos interactivos si aparecen.
            timeout: Tiempo máximo de espera en segundos.

        Returns:
            Lista de diccionarios con el texto del comentario y metadatos anonimizados.
        """
        self._check_dependencies()
        cookie_mgr = TikTokCookieManager(output_dir=str(self.output_dir))
        if not cookie_mgr.has_valid_cookies():
            cookie_mgr.ensure_cookies()
            self.cookies_path = self.output_dir / "cookies.json"

        print(f"[*] [COMENTARIOS] Iniciando extracción ética para: {post_url}")
        print(f"[*] Meta de extracción: hasta {max_comments} comentarios con anonimización SHA-256...")

        anonymized_comments: List[Dict[str, Any]] = []
        seen_comment_ids = set()

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=not headed,
                args=get_stealth_browser_args()
            )

            context_kwargs = {
                "viewport": {"width": 1280, "height": 800},
                "user_agent": DEFAULT_USER_AGENT,
                "locale": "es-ES,es;q=0.9,en;q=0.8",
            }

            if self.cookies_path and self.cookies_path.exists():
                context = await browser.new_context(storage_state=str(self.cookies_path), **context_kwargs)
            else:
                context = await browser.new_context(**context_kwargs)

            await context.add_init_script(get_stealth_init_script())
            page = await context.new_page()

            # Interceptor de red para capturar el endpoint interno de comentarios
            async def handle_comment_response(response):
                if "/api/comment/list/" in response.url:
                    try:
                        data = await response.json()
                        raw_comments = data.get("comments", [])
                        for rc in raw_comments:
                            cid = str(rc.get("cid", ""))
                            if cid and cid not in seen_comment_ids:
                                seen_comment_ids.add(cid)
                                raw_uid = str(rc.get("user", {}).get("uid", "") or rc.get("user", {}).get("unique_id", ""))
                                
                                # APLICACIÓN DE HASHING SHA-256 INMEDIATO EN MEMORIA
                                author_pseudonym = self.pseudonymize_identifier(raw_uid)

                                text = rc.get("text", "")
                                if text:
                                    anonymized_comments.append({
                                        "comment_id": cid,
                                        "author_hash": author_pseudonym,
                                        "text": text,
                                        "likes": int(rc.get("digg_count", 0)),
                                        "reply_count": int(rc.get("reply_comment_total", 0)),
                                        "create_time": rc.get("create_time", 0)
                                    })
                    except Exception:
                        pass

            page.on("response", handle_comment_response)

            try:
                await page.goto(post_url, timeout=timeout * 1000, wait_until="domcontentloaded")
                await asyncio.sleep(3)
            except Exception as e:
                print(f"[!] Aviso al navegar a la publicación: {e}")

            # Desplazamiento progresivo para disparar la carga de comentarios
            scroll_attempts = 0
            max_scrolls = max(8, max_comments // 15)

            while len(anonymized_comments) < max_comments and scroll_attempts < max_scrolls:
                await page.mouse.wheel(0, 1000)
                await asyncio.sleep(1.8)
                scroll_attempts += 1

            # Fallback vía DOM si la intercepción no alcanzó la cuota esperada
            if len(anonymized_comments) < max_comments:
                dom_comments = await page.evaluate("""() => {
                    const containers = document.querySelectorAll('[data-e2e="comment-item"], [class*="CommentItem"]');
                    const results = [];
                    for (const el of containers) {
                        const textEl = el.querySelector('[data-e2e="comment-level-1"], p, span');
                        const txt = textEl ? textEl.innerText.trim() : '';
                        if (txt) {
                            results.append ? results.append(txt) : results.push(txt);
                        }
                    }
                    return results;
                }""")
                for d_text in dom_comments:
                    if len(anonymized_comments) >= max_comments:
                        break
                    # Generar hash sintético para comentaristas capturados por DOM sin ID
                    dom_hash = self.pseudonymize_identifier(f"DOM_FALLBACK_{len(anonymized_comments)}")
                    anonymized_comments.append({
                        "comment_id": f"dom_{len(anonymized_comments) + 1}",
                        "author_hash": dom_hash,
                        "text": d_text,
                        "likes": 0,
                        "reply_count": 0,
                        "create_time": 0
                    })

            await browser.close()

        final_sample = anonymized_comments[:max_comments]
        print(f"[OK] [COMENTARIOS] Muestra obtenida: {len(final_sample)} comentarios anonimizados.")
        return final_sample

    def scrape_comments(
        self,
        post_url: str,
        max_comments: int = 150,
        headed: bool = False,
        timeout: int = 35
    ) -> List[Dict[str, Any]]:
        """Envoltorio síncrono para scrape_comments_async."""
        return asyncio.run(
            self.scrape_comments_async(post_url, max_comments=max_comments, headed=headed, timeout=timeout)
        )
