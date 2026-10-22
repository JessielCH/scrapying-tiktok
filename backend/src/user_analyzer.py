"""
Módulo de Análisis de Perfiles y Publicaciones de TikTok
=========================================================
Proporciona la extracción automatizada del perfil y el cálculo estadístico
de métricas de engagement para videos y carruseles fotográficos en TikTok.
"""

import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    from playwright.async_api import async_playwright
except ImportError:
    async_playwright = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

from .utils import ensure_output_dir
from .anti_detect import DEFAULT_USER_AGENT, get_stealth_browser_args, get_stealth_init_script
from .cookie_manager import TikTokCookieManager


class TikTokUserAnalyzer:
    """
    Extrae la información pública del perfil de usuario y calcula métricas
    numéricas y estadísticas de rendimiento sobre sus publicaciones recientes
    (compatible con publicaciones de video y carruseles fotográficos).
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

    def _clean_username(self, raw_input: str) -> str:
        """Limpia el prefijo '@' o extrae el identificador único a partir de la URL del perfil."""
        cleaned = raw_input.strip()
        if "tiktok.com/@" in cleaned:
            cleaned = cleaned.split("tiktok.com/@")[-1].split("?")[0].split("/")[0]
        elif cleaned.startswith("@"):
            cleaned = cleaned[1:]
        return cleaned

    def _check_dependencies(self):
        missing = []
        if async_playwright is None:
            missing.append("playwright")
        if BeautifulSoup is None:
            missing.append("beautifulsoup4")
        if missing:
            raise RuntimeError(
                f"Dependencias faltantes: {', '.join(missing)}. "
                f"Por favor instala ejecutando: pip install {' '.join(missing)}"
            )

    def _extract_post_media_and_type(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detecta si la publicación es un video estándar o un carrusel de diapositivas,
        extrayendo las URLs de las imágenes o el enlace directo del flujo de video.
        """
        # 1. Comprobar estructuras de carrusel (imagePostInfo, imagePost, images)
        image_post = item.get("imagePostInfo") or item.get("imagePost") or {}
        images_raw = image_post.get("images") or []
        if not images_raw and "images" in item and isinstance(item["images"], list):
            images_raw = item["images"]

        image_urls: List[str] = []
        if images_raw:
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

        video_info = item.get("video") or {}
        video_url = video_info.get("playAddr") or video_info.get("downloadAddr") or ""

        if image_urls or image_post:
            post_type = "carousel"
        else:
            post_type = "video"

        return {
            "post_type": post_type,
            "is_carousel": post_type == "carousel",
            "carousel_images_count": len(image_urls),
            "carousel_images": image_urls,
            "video_stream_url": video_url if post_type == "video" else ""
        }

    async def analyze_user_async(
        self,
        username: str,
        max_videos: int = 10,
        headed: bool = False,
        timeout: int = 40
    ) -> Dict[str, Any]:
        """
        Consulta de forma asíncrona el perfil del usuario y extrae sus publicaciones
        recientes (videos y carruseles) calculando métricas numéricas agregadas.
        """
        self._check_dependencies()
        handle = self._clean_username(username)
        profile_url = f"https://www.tiktok.com/@{handle}"

        # Enforce cookies
        cookie_mgr = TikTokCookieManager(output_dir=str(self.output_dir))
        if not cookie_mgr.has_valid_cookies():
            print("\n[OBLIGATORIO] Se requiere una sesion con cookies para evitar 'Acceso Denegado'.")
            cookie_mgr.ensure_cookies()
            self.cookies_path = self.output_dir / "cookies.json"

        print(f"[*] Analizando usuario de TikTok: @{handle}")
        print(f"[*] Enlace del perfil: {profile_url}")

        async with async_playwright() as p:
            launch_args = get_stealth_browser_args()
            browser = await p.chromium.launch(headless=not headed, args=launch_args)

            context_kwargs = {
                "viewport": {"width": 1920, "height": 1080},
                "user_agent": DEFAULT_USER_AGENT,
                "locale": "es-ES,es;q=0.9,en;q=0.8",
            }
            if self.cookies_path and self.cookies_path.exists():
                print(f"[INFO] Inyectando cookies obligatorias desde: {self.cookies_path}")
                try:
                    context = await browser.new_context(storage_state=str(self.cookies_path), **context_kwargs)
                except Exception as e:
                    print(f"[!] Error leyendo cookies ({e}). Obteniendo sesion limpia...")
                    cookie_mgr.ensure_cookies()
                    context = await browser.new_context(storage_state=str(self.output_dir / "cookies.json"), **context_kwargs)
            else:
                cookie_mgr.ensure_cookies()
                context = await browser.new_context(storage_state=str(self.output_dir / "cookies.json"), **context_kwargs)

            await context.add_init_script(get_stealth_init_script())
            page = await context.new_page()

            # Network interception for post item list
            intercepted_items: List[Dict[str, Any]] = []

            async def handle_response(res):
                if "/api/post/item_list/" in res.url:
                    try:
                        data = await res.json()
                        items = data.get("itemList", [])
                        if items:
                            intercepted_items.extend(items)
                    except Exception:
                        pass

            page.on("response", handle_response)

            print("[*] Cargando página del perfil...")
            try:
                await page.goto(profile_url, timeout=timeout * 1000, wait_until="commit")
            except Exception as e:
                print(f"[!] Aviso al cargar la página: {e}")

            await asyncio.sleep(4)

            # Extraer metadatos de perfil de la etiqueta SSR
            profile_data = await page.evaluate("""() => {
                const el = document.getElementById('__UNIVERSAL_DATA_FOR_REHYDRATION__');
                if (!el) return null;
                try {
                    const data = JSON.parse(el.innerText);
                    const scope = data['__DEFAULT_SCOPE__'] || {};
                    const userDetail = scope['webapp.user-detail'] || {};
                    const userInfo = userDetail['userInfo'] || {};
                    return {
                        user: userInfo['user'] || null,
                        stats: userInfo['stats'] || null
                    };
                } catch (e) {
                    return null;
                }
            }""")

            user_obj = (profile_data or {}).get("user") or {}
            stats_obj = (profile_data or {}).get("stats") or {}

            # Parseo secundario mediante DOM si SSR no está presente
            if not user_obj:
                print("[*] Etiqueta SSR no encontrada, extrayendo elementos del DOM...")
                dom_info = await page.evaluate("""() => {
                    const getTxt = (sel) => {
                        const el = document.querySelector(sel);
                        return el ? el.innerText.trim() : '';
                    };
                    return {
                        title: getTxt('[data-e2e="user-title"]'),
                        subtitle: getTxt('[data-e2e="user-subtitle"]'),
                        bio: getTxt('[data-e2e="user-bio"]'),
                        following: getTxt('[data-e2e="following-count"]'),
                        followers: getTxt('[data-e2e="followers-count"]'),
                        likes: getTxt('[data-e2e="likes-count"]')
                    };
                }""")
                user_obj = {
                    "uniqueId": dom_info.get("subtitle") or handle,
                    "nickname": dom_info.get("title") or handle,
                    "signature": dom_info.get("bio", ""),
                    "verified": False,
                    "secUid": "",
                }
                stats_obj = {
                    "followingCount": dom_info.get("following", "0"),
                    "followerCount": dom_info.get("followers", "0"),
                    "heartCount": dom_info.get("likes", "0"),
                    "videoCount": 0
                }

            async def is_captcha_active():
                return await page.evaluate("""() => {
                    const el = document.querySelector('.captcha-disable-scroll, [class*="captcha"], #captcha_container, #verify-bar, .verify-wrap');
                    return el !== null;
                }""")

            # Si TikTok desplegó el captcha del rompecabezas
            if await is_captcha_active():
                if headed:
                    print("\n" + "=" * 68)
                    print("[CAPTCHA DETECTADO] TikTok desplegó un rompecabezas de verificación.")
                    print("Por favor, arrastra la pieza del rompecabezas en la ventana del navegador.")
                    print("Esperando hasta 60 segundos a que resuelvas el desafío...")
                    print("=" * 68 + "\n")
                    
                    solved = False
                    for i in range(60):
                        await asyncio.sleep(1)
                        if not await is_captcha_active():
                            solved = True
                            print("[OK] Rompecabezas resuelto exitosamente. Cargando publicaciones...\n")
                            await asyncio.sleep(3)
                            break
                    if not solved:
                        print("[!] Tiempo de espera agotado para resolver el captcha.")
                else:
                    print("\n[!] AVISO: TikTok bloqueó la carga de publicaciones con un captcha.")
                    print("[!] Solución: Responde 's' para abrir la ventana y resolverlo,")
                    print("    o inicia sesión una vez con la Opción [2] (Login QR) para evitar captchas.\n")

            # Desplazamiento para cargar la cuadrícula de publicaciones
            print("[*] Desplazando página para cargar publicaciones recientes (videos y carruseles)...")
            for scroll_step in range(6):
                if len(intercepted_items) >= max_videos:
                    break
                await page.mouse.wheel(0, 1200)
                await asyncio.sleep(2)

            # Si durante el scroll apareció el captcha nuevamente y la ventana está visible
            if len(intercepted_items) == 0 and await is_captcha_active() and headed:
                print("\n[!] El rompecabezas de verificación sigue activo en la ventana.")
                print("[*] Por favor completa el deslizador en la ventana abierta...")
                for i in range(45):
                    await asyncio.sleep(1)
                    if not await is_captcha_active():
                        print("[OK] Rompecabezas resuelto. Desplazando cuadrícula...\n")
                        await asyncio.sleep(2)
                        for _ in range(4):
                            await page.mouse.wheel(0, 1200)
                            await asyncio.sleep(1.5)
                        break

            # Comprobar también el DOM si la intercepción de red no capturó suficientes
            if len(intercepted_items) < max_videos:
                dom_posts = await page.evaluate("""() => {
                    const anchors = Array.from(document.querySelectorAll('a[href*="/video/"], a[href*="/photo/"]'));
                    const seen = new Set();
                    const list = [];
                    for (const a of anchors) {
                        const href = a.href;
                        if (!seen.has(href)) {
                            seen.add(href);
                            const idMatch = href.match(/\\/(video|photo)\\/(\\d+)/);
                            const postType = href.includes('/photo/') ? 'carousel' : 'video';
                            const id = idMatch ? idMatch[2] : '';
                            list.push({
                                id: id,
                                url: href,
                                desc: a.innerText || '',
                                postType: postType
                            });
                        }
                    }
                    return list;
                }""")
                existing_ids = {str(item.get("id")) for item in intercepted_items}
                for dp in dom_posts:
                    if dp["id"] and dp["id"] not in existing_ids:
                        intercepted_items.append({
                            "id": dp["id"],
                            "desc": dp.get("desc", ""),
                            "imagePostInfo": {"images": []} if dp.get("postType") == "carousel" else None,
                            "stats": {"diggCount": 0, "commentCount": 0, "collectCount": 0, "shareCount": 0, "playCount": 0}
                        })

            await browser.close()

            # Procesar y formatear las últimas N publicaciones (videos y carruseles)
            processed_posts: List[Dict[str, Any]] = []
            selected_items = intercepted_items[:max_videos]

            for item in selected_items:
                post_id = str(item.get("id", ""))
                st = item.get("stats", {})
                media_info = self._extract_post_media_and_type(item)

                processed_posts.append({
                    "id": post_id,
                    "type": media_info["post_type"],  # 'video' o 'carousel'
                    "is_carousel": media_info["is_carousel"],
                    "url": f"https://www.tiktok.com/@{handle}/video/{post_id}" if post_id else "",
                    "description": item.get("desc", ""),
                    "create_time": item.get("createTime", 0),
                    "likes": int(st.get("diggCount", 0)),
                    "comments": int(st.get("commentCount", 0)),
                    "saves": int(st.get("collectCount", 0)),
                    "shares": int(st.get("shareCount", 0)),
                    "views": int(st.get("playCount", 0)),
                    "carousel_images_count": media_info["carousel_images_count"],
                    "carousel_images": media_info["carousel_images"],
                    "video_stream_url": media_info["video_stream_url"],
                })

            # Cálculos del análisis numérico
            total_posts_analyzed = len(processed_posts)
            total_videos_count = sum(1 for p in processed_posts if p["type"] == "video")
            total_carousels_count = sum(1 for p in processed_posts if p["type"] == "carousel")
            total_carousel_images = sum(p["carousel_images_count"] for p in processed_posts)

            total_likes = sum(p["likes"] for p in processed_posts)
            total_comments = sum(p["comments"] for p in processed_posts)
            total_saves = sum(p["saves"] for p in processed_posts)
            total_shares = sum(p["shares"] for p in processed_posts)
            total_views = sum(p["views"] for p in processed_posts)
            total_engagements = total_likes + total_comments + total_saves + total_shares

            avg_likes = round(total_likes / total_posts_analyzed, 2) if total_posts_analyzed > 0 else 0
            avg_comments = round(total_comments / total_posts_analyzed, 2) if total_posts_analyzed > 0 else 0
            avg_saves = round(total_saves / total_posts_analyzed, 2) if total_posts_analyzed > 0 else 0
            avg_shares = round(total_shares / total_posts_analyzed, 2) if total_posts_analyzed > 0 else 0
            avg_views = round(total_views / total_posts_analyzed, 2) if total_posts_analyzed > 0 else 0

            # Tasa de interacción (Engagement Rate % basada en reproducciones)
            engagement_rate_views = (
                round((total_engagements / total_views) * 100, 2) if total_views > 0 else 0.0
            )

            # Publicaciones con mayor rendimiento
            top_post_by_views = max(processed_posts, key=lambda p: p["views"]) if processed_posts else None
            top_post_by_likes = max(processed_posts, key=lambda p: p["likes"]) if processed_posts else None

            # Valores numéricos del perfil
            followers_raw = stats_obj.get("followerCount", 0)
            following_raw = stats_obj.get("followingCount", 0)
            heart_raw = stats_obj.get("heartCount", 0)
            video_count_raw = stats_obj.get("videoCount", 0)

            def parse_num(val):
                if isinstance(val, (int, float)):
                    return int(val)
                s = str(val).upper().replace(",", "").strip()
                try:
                    if "M" in s:
                        return int(float(s.replace("M", "")) * 1_000_000)
                    if "K" in s:
                        return int(float(s.replace("K", "")) * 1_000)
                    if "B" in s:
                        return int(float(s.replace("B", "")) * 1_000_000_000)
                    return int(s)
                except Exception:
                    return 0

            analysis_result = {
                "profile": {
                    "username": f"@{user_obj.get('uniqueId', handle)}",
                    "nickname": user_obj.get("nickname", ""),
                    "biography": user_obj.get("signature", ""),
                    "verified": bool(user_obj.get("verified", False)),
                    "sec_uid": user_obj.get("secUid", ""),
                    "following_count": parse_num(following_raw),
                    "follower_count": parse_num(followers_raw),
                    "total_likes_received": parse_num(heart_raw),
                    "total_videos_count": parse_num(video_count_raw),
                },
                "posts_analysis": {
                    "sample_size": total_posts_analyzed,
                    "post_types": {
                        "videos_count": total_videos_count,
                        "carousels_count": total_carousels_count,
                        "total_carousel_images": total_carousel_images,
                    },
                    "metrics_totals": {
                        "likes": total_likes,
                        "comments": total_comments,
                        "saves": total_saves,
                        "shares": total_shares,
                        "views": total_views,
                        "total_interactions": total_engagements,
                    },
                    "metrics_averages": {
                        "avg_likes": avg_likes,
                        "avg_comments": avg_comments,
                        "avg_saves": avg_saves,
                        "avg_shares": avg_shares,
                        "avg_views": avg_views,
                    },
                    "performance": {
                        "engagement_rate_percent": engagement_rate_views,
                        "best_post_id_by_views": (top_post_by_views or {}).get("id", ""),
                        "best_post_id_by_likes": (top_post_by_likes or {}).get("id", ""),
                    },
                    "posts": processed_posts
                }
            }

            return analysis_result

    def analyze_user(
        self,
        username: str,
        max_videos: int = 10,
        headed: bool = False,
        timeout: int = 40
    ) -> Dict[str, Any]:
        """Envoltorio síncrono para analyze_user_async."""
        return asyncio.run(
            self.analyze_user_async(username, max_videos=max_videos, headed=headed, timeout=timeout)
        )
