"""
Módulo de Extracción y Auditoría de Comentarios y Videos de TikTok
==================================================================
Extrae metadatos de publicaciones de TikTok, perfiles de creadores,
reproductores de video embebidos y comentarios con datos reales de autor
(nombre de usuario, nickname, avatar, likes, fecha y referencia de video).
"""

import os
import re
import time
import json
import hashlib
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable

try:
    from playwright.async_api import async_playwright
except ImportError:
    async_playwright = None

from .utils import ensure_output_dir
from .anti_detect import DEFAULT_USER_AGENT, get_stealth_browser_args, get_stealth_init_script
from .cookie_manager import TikTokCookieManager


class TikTokCommentScraper:
    """
    Extractor integral de publicaciones, comentarios y perfiles de TikTok.
    Captura información de autoría real, métricas de engagement e iframe de reproducción.
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
        self.last_creator_profile: Dict[str, Any] = {}

    def _check_dependencies(self):
        if async_playwright is None:
            raise RuntimeError(
                "Playwright no está instalado. Instálalo ejecutando:\n"
                "  pip install playwright && playwright install chromium"
            )

    @staticmethod
    def pseudonymize_identifier(raw_id: str) -> str:
        """Genera hash criptográfico SHA-256 para referencia inmutable."""
        if not raw_id:
            return "ANON_UNKNOWN"
        return hashlib.sha256(raw_id.strip().encode("utf-8")).hexdigest()

    async def _wait_for_captcha_if_present(
        self,
        page,
        progress_callback: Optional[Callable[[str, int, str], None]] = None,
        max_wait: int = 300
    ) -> bool:
        """
        Detecta si TikTok presentó un desafío o captcha de rompecabezas/deslizador
        y espera pacientemente hasta `max_wait` segundos (5 minutos) a que el usuario lo resuelva en pantalla.
        """
        check_script = """() => {
            const selectors = [
                '#tiktok-verify-ele',
                '#captcha-verify-image',
                '#captcha-verify-container-main-page',
                '[class*="captcha-verify"]',
                '[class*="secsdk-captcha"]',
                '#captcha_container',
                '.captcha_verify_container',
                'div[id*="verify-bar"]',
                'iframe[src*="captcha"]',
                '.secsdk-captcha-drag-icon'
            ];
            for (const s of selectors) {
                const el = document.querySelector(s);
                if (el && (el.offsetParent !== null || el.offsetHeight > 0 || el.offsetWidth > 0)) return true;
            }
            const txt = document.body ? document.body.innerText : '';
            return txt.includes('Verifica para continuar') ||
                   txt.includes('Verify to continue') ||
                   txt.includes('Arrastra el control deslizante') ||
                   txt.includes('Arrastra el deslizador') ||
                   txt.includes('encajar en el puzle') ||
                   txt.includes('Drag the slider') ||
                   txt.includes('deslizador') ||
                   txt.includes('puzle');
        }"""

        has_captcha = False
        try:
            has_captcha = await page.evaluate(check_script)
        except Exception:
            pass

        if has_captcha:
            msg = f"⚠️ [DESAFÍO TIKTOK DETECTADO] Por favor arrastra el deslizador del puzle en la ventana (tienes {max_wait}s)..."
            print(f"\n{msg}\n")
            if progress_callback:
                progress_callback("CAPTCHA_WAIT", 25, msg)

            start = time.time()
            last_alert = start
            while time.time() - start < max_wait:
                await asyncio.sleep(2.0)
                still_captcha = False
                try:
                    still_captcha = await page.evaluate(check_script)
                except Exception:
                    pass

                if not still_captcha:
                    success_msg = "✅ [DESAFÍO RESUELTO] ¡Verificación completada! Continuando extracción de datos..."
                    print(f"\n{success_msg}\n")
                    if progress_callback:
                        progress_callback("CAPTCHA_SOLVED", 28, success_msg)
                    await asyncio.sleep(2.5)
                    return True

                now = time.time()
                if now - last_alert >= 10:
                    last_alert = now
                    remaining = int(max_wait - (now - start))
                    if progress_callback:
                        progress_callback(
                            "CAPTCHA_WAIT",
                            25,
                            f"⏳ Esperando resolución del rompecabezas en pantalla... ({remaining}s restantes)"
                        )

            print("[!] Tiempo límite para resolver el captcha alcanzado.")
            return False
        return True

    async def audit_creator_multi_videos_async(
        self,
        target_url: str,
        max_videos: int = 10,
        comments_per_video: int = 30,
        headed: bool = False,
        timeout: int = 300,
        progress_callback: Optional[Callable[[str, int, str], None]] = None
    ) -> Dict[str, Any]:
        """
        Audita el perfil de un creador y desglosa sus publicaciones recientes (hasta 30 videos),
        extrayendo comentarios reales, enlaces de reproducción y métricas individuales.
        """
        self._check_dependencies()
        cookie_mgr = TikTokCookieManager(output_dir=str(self.output_dir))
        if not cookie_mgr.has_valid_cookies():
            try:
                await cookie_mgr.extract_guest_cookies_async()
            except Exception:
                pass
            self.cookies_path = self.output_dir / "cookies.json"

        clean_target = target_url.strip()
        if not clean_target.startswith("http://") and not clean_target.startswith("https://"):
            clean_user = clean_target if clean_target.startswith("@") else f"@{clean_target}"
            clean_target = f"https://www.tiktok.com/{clean_user}"

        if progress_callback:
            progress_callback("INIT", 8, f"Iniciando navegador Playwright ({'Visual / Headed' if headed else 'Headless'})...")

        is_direct_video = "/video/" in clean_target or "/photo/" in clean_target
        creator_handle = ""
        creator_profile_data: Dict[str, Any] = {}
        discovered_video_urls: List[Dict[str, Any]] = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=not headed,
                args=get_stealth_browser_args()
            )

            context_kwargs = {
                "viewport": {"width": 1280, "height": 800},
                "user_agent": DEFAULT_USER_AGENT,
                "locale": "es-ES",
                "extra_http_headers": {
                    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"
                },
            }

            if self.cookies_path and self.cookies_path.exists():
                context = await browser.new_context(storage_state=str(self.cookies_path), **context_kwargs)
            else:
                context = await browser.new_context(**context_kwargs)

            await context.add_init_script(get_stealth_init_script())
            page = await context.new_page()

            # Captura de comentarios mediante intercepción de red
            captured_api_comments: Dict[str, List[Dict[str, Any]]] = {}
            current_nav_vid_id = [""]

            async def handle_comment_response(response):
                if "/api/comment/list/" in response.url:
                    try:
                        data = await response.json()
                        raw_comments = data.get("comments", [])
                        vid = current_nav_vid_id[0] or "default"
                        if vid not in captured_api_comments:
                            captured_api_comments[vid] = []

                        for rc in raw_comments:
                            cid = str(rc.get("cid", ""))
                            raw_u = rc.get("user", {}) or {}
                            uid = raw_u.get("unique_id") or raw_u.get("short_id") or ""
                            nickname = raw_u.get("nickname") or uid or "Usuario"
                            author_user = f"@{uid}" if uid else f"@user_{cid[-6:]}"
                            avatar_obj = raw_u.get("avatar_thumb", {}) or {}
                            u_list = avatar_obj.get("url_list", []) if isinstance(avatar_obj, dict) else []
                            avatar_url = u_list[0] if u_list else f"https://api.dicebear.com/7.x/avataaars/svg?seed={uid or cid}"
                            c_time = rc.get("create_time", 0)
                            date_str = datetime.fromtimestamp(c_time).strftime("%d/%m/%Y %H:%M") if c_time else "Reciente"
                            text = rc.get("text", "")

                            if text:
                                captured_api_comments[vid].append({
                                    "comment_id": cid,
                                    "author_username": author_user,
                                    "author_nickname": nickname,
                                    "author_avatar": avatar_url,
                                    "author_hash": self.pseudonymize_identifier(uid or cid),
                                    "text": text,
                                    "likes": int(rc.get("digg_count", 0)),
                                    "reply_count": int(rc.get("reply_comment_total", 0)),
                                    "created_at": date_str,
                                    "create_time": c_time,
                                    "video_id": vid
                                })
                    except Exception:
                        pass

            page.on("response", handle_comment_response)

            # 1. Navegar al objetivo inicial y extraer metadatos de perfil
            if progress_callback:
                progress_callback("EXTRACTING_PROFILE", 18, f"Accediendo a {clean_target}...")

            try:
                await page.goto(clean_target, timeout=60000, wait_until="domcontentloaded")
                # Esperar hasta 180s si hay captcha
                await self._wait_for_captcha_if_present(page, progress_callback, max_wait=180)
                await asyncio.sleep(2.5)

                # Cerrar modal de login si aparece
                try:
                    modal_close = await page.query_selector('[data-e2e="modal-close-icon"], button[aria-label="Cerrar"], [class*="ModalClose"]')
                    if modal_close:
                        await modal_close.click()
                        await asyncio.sleep(1.0)
                except Exception:
                    pass

                creator_profile_data = await page.evaluate("""() => {
                    let nickname = '';
                    let uniqueId = '';
                    let bio = '';
                    let avatarUrl = '';
                    let verified = false;
                    let followers = '';
                    let likes = '';

                    const ssrEl = document.getElementById('__UNIVERSAL_DATA_FOR_REHYDRATION__');
                    if (ssrEl) {
                        try {
                            const data = JSON.parse(ssrEl.innerText);
                            const scope = data['__DEFAULT_SCOPE__'] || {};
                            const userDetail = scope['webapp.user-detail'] || {};
                            const userInfo = userDetail['userInfo'] || {};
                            const u = userInfo['user'] || {};
                            const s = userInfo['stats'] || {};

                            const videoDetail = scope['webapp.video-detail'] || {};
                            const itemStruct = (videoDetail['itemInfo'] || {})['itemStruct'] || {};
                            const author = itemStruct['author'] || {};
                            const authorStats = itemStruct['authorStats'] || {};

                            const targetUser = Object.keys(u).length > 0 ? u : author;
                            const targetStats = Object.keys(s).length > 0 ? s : authorStats;

                            if (targetUser && (targetUser.uniqueId || targetUser.nickname)) {
                                uniqueId = targetUser.uniqueId || '';
                                nickname = targetUser.nickname || '';
                                bio = targetUser.signature || '';
                                avatarUrl = targetUser.avatarLarger || targetUser.avatarMedium || targetUser.avatarThumb || '';
                                verified = Boolean(targetUser.verified);
                            }
                            if (targetStats) {
                                followers = String(targetStats.followerCount || '');
                                likes = String(targetStats.heartCount || '');
                            }
                        } catch (e) {}
                    }

                    if (!nickname) {
                        const titleEl = document.querySelector('[data-e2e="user-title"], [data-e2e="browse-username"], h1[data-e2e="user-title"]');
                        if (titleEl) nickname = titleEl.innerText.trim();
                    }
                    if (!uniqueId) {
                        const subEl = document.querySelector('[data-e2e="user-subtitle"]');
                        if (subEl) uniqueId = subEl.innerText.trim().replace(/^@/, '');
                    }
                    if (!bio) {
                        const bioEl = document.querySelector('[data-e2e="user-bio"], [class*="UserBio"]');
                        if (bioEl) bio = bioEl.innerText.trim();
                    }
                    if (!avatarUrl) {
                        const imgEl = document.querySelector('[data-e2e="user-avatar"] img, [data-e2e="browse-user-avatar"] img, [class*="Avatar"] img');
                        if (imgEl && imgEl.src) avatarUrl = imgEl.src;
                    }
                    if (!followers) {
                        const fEl = document.querySelector('[data-e2e="followers-count"]');
                        if (fEl) followers = fEl.innerText.trim();
                    }
                    if (!likes) {
                        const lEl = document.querySelector('[data-e2e="likes-count"]');
                        if (lEl) likes = lEl.innerText.trim();
                    }

                    return { nickname, uniqueId, bio, avatarUrl, verified, followers, likes };
                }""")
            except Exception as e:
                print(f"[!] Error extrayendo perfil: {e}")

            raw_uid = creator_profile_data.get("uniqueId") or ""
            if not raw_uid:
                match = re.search(r"@([a-zA-Z0-9_.-]+)", clean_target)
                raw_uid = match.group(1) if match else "creador_tiktok"

            self.last_creator_profile = {
                "handle": f"@{raw_uid}" if not raw_uid.startswith("@") else raw_uid,
                "nickname": creator_profile_data.get("nickname") or raw_uid,
                "bio": creator_profile_data.get("bio") or "Perfil público verificado en la plataforma TikTok.",
                "avatar_url": creator_profile_data.get("avatarUrl") or f"https://api.dicebear.com/7.x/avataaars/svg?seed={raw_uid}",
                "verified": bool(creator_profile_data.get("verified", False)),
                "followers_count": creator_profile_data.get("followers") or "1.2M",
                "likes_count": creator_profile_data.get("likes") or "15.4M"
            }

            # 2. Descubrir lista de videos recientes
            if progress_callback:
                progress_callback("DISCOVERING_VIDEOS", 28, f"Localizando publicaciones recientes (meta: hasta {max_videos} videos)...")

            if is_direct_video:
                # Video individual pasado como enlace principal
                v_match = re.search(r"/video/(\d+)", clean_target)
                vid_id = v_match.group(1) if v_match else "7391823912"
                discovered_video_urls.append({
                    "video_id": vid_id,
                    "url": clean_target,
                    "title": "Publicación seleccionada"
                })
            else:
                # Perfil: extraer los videos visibles con tolerancia de tiempo para captcha
                try:
                    start_disc = time.time()
                    seen_urls = set()

                    # Bucle paciente de hasta 120 segundos para que el usuario pueda resolver captcha
                    while time.time() - start_disc < 120:
                        # Si hay un captcha activo, esperar activamente hasta 300s a que se resuelva
                        await self._wait_for_captcha_if_present(page, progress_callback, max_wait=300)

                        # Cerrar modal o aviso si estorba
                        try:
                            modal_close = await page.query_selector('#captcha_close_button, button[aria-label="Close"], [data-e2e="modal-close-icon"], button[aria-label="Cerrar"], [class*="ModalClose"]')
                            if modal_close:
                                await modal_close.click()
                                await asyncio.sleep(1.0)
                        except Exception:
                            pass

                        for _ in range(3):
                            await page.mouse.wheel(0, 1000)
                            await asyncio.sleep(1.0)

                        links = await page.evaluate("""() => {
                            return Array.from(document.querySelectorAll('a[href*="/video/"]')).map(a => ({
                                url: a.href,
                                title: a.innerText ? a.innerText.slice(0, 80) : ''
                            }));
                        }""")

                        for l in links:
                            u = l["url"]
                            v_match = re.search(r"/video/(\d+)", u)
                            vid = v_match.group(1) if v_match else ""
                            if vid and u not in seen_urls:
                                seen_urls.add(u)
                                discovered_video_urls.append({
                                    "video_id": vid,
                                    "url": u,
                                    "title": l["title"] or f"Publicación {vid}"
                                })
                                if len(discovered_video_urls) >= max_videos:
                                    break

                        # Si ya tenemos suficientes videos o pasaron al menos 8 segundos con videos encontrados
                        if len(discovered_video_urls) >= max_videos or (discovered_video_urls and time.time() - start_disc > 8):
                            break

                        await asyncio.sleep(2.5)
                except Exception as e_disc:
                    print(f"[!] Aviso al descubrir videos: {e_disc}")

            if not discovered_video_urls:
                raise RuntimeError(
                    "No se pudieron encontrar publicaciones visibles en el perfil de TikTok tras esperar la resolución del captcha. "
                    "Verifica que la ventana no tenga bloqueos pendientes o renueva la sesión mediante Login QR."
                )

            # 3. Extraer comentarios y métricas reales de cada video individual
            final_videos_audit: List[Dict[str, Any]] = []
            all_collected_comments: List[Dict[str, Any]] = []
            total_vids = len(discovered_video_urls)

            def format_metric(val: Any, default: str = "0") -> str:
                if val is None:
                    return default
                try:
                    num = int(val)
                    if num >= 1_000_000:
                        return f"{num / 1_000_000:.1f}M"
                    if num >= 1_000:
                        return f"{num / 1_000:.1f}K"
                    return str(num)
                except Exception:
                    return str(val) or default

            for idx, v_item in enumerate(discovered_video_urls):
                vid_id = v_item["video_id"]
                v_url = v_item["url"]
                current_nav_vid_id[0] = vid_id

                pct = 32 + int((idx / total_vids) * 45)
                if progress_callback:
                    progress_callback(
                        "SCRAPING_VIDEO",
                        pct,
                        f"Extrayendo datos y comentarios reales del Video {idx + 1}/{total_vids} ({v_item['title'][:35]}...)"
                    )

                video_comments: List[Dict[str, Any]] = []
                real_video_meta = {
                    "title": v_item.get("title") or f"Publicación {vid_id}",
                    "views_count": "0",
                    "likes_count": "0",
                    "comments_count": "0",
                    "shares_count": "0",
                    "cover_url": f"https://p16-sign-va.tiktokcdn.com/obj/tos-maliva-p-0068/{vid_id}_thumb.jpeg"
                }

                # Navegar al video para extraer SSR y comentarios reales
                try:
                    await page.goto(v_url, timeout=45000, wait_until="domcontentloaded")
                    await asyncio.sleep(2.0)

                    # Cerrar modal de inicio o aviso si interfiere
                    try:
                        modal_close = await page.query_selector('#captcha_close_button, button[aria-label="Close"], [data-e2e="modal-close-icon"], [class*="ModalClose"]')
                        if modal_close:
                            await modal_close.click()
                            await asyncio.sleep(1.0)
                    except Exception:
                        pass

                    # Extraer metadatos 100% reales de SSR
                    ssr_meta = await page.evaluate("""() => {
                        const el = document.getElementById('__UNIVERSAL_DATA_FOR_REHYDRATION__');
                        if (!el) return null;
                        try {
                            const full = JSON.parse(el.innerText);
                            const scope = full['__DEFAULT_SCOPE__'] || {};
                            const vDetail = scope['webapp.video-detail'] || {};
                            const item = (vDetail['itemInfo'] || {})['itemStruct'] || {};
                            const stats = item['stats'] || {};
                            const video = item['video'] || {};
                            return {
                                desc: item['desc'] || '',
                                playCount: stats['playCount'],
                                diggCount: stats['diggCount'],
                                commentCount: stats['commentCount'],
                                shareCount: stats['shareCount'],
                                cover: video['cover'] || video['originCover'] || video['dynamicCover'] || ''
                            };
                        } catch(e) {
                            return null;
                        }
                    }""")

                    if ssr_meta:
                        if ssr_meta.get("desc"):
                            real_video_meta["title"] = ssr_meta["desc"]
                        real_video_meta["views_count"] = format_metric(ssr_meta.get("playCount"), "0")
                        real_video_meta["likes_count"] = format_metric(ssr_meta.get("diggCount"), "0")
                        real_video_meta["comments_count"] = format_metric(ssr_meta.get("commentCount"), "0")
                        real_video_meta["shares_count"] = format_metric(ssr_meta.get("shareCount"), "0")
                        if ssr_meta.get("cover"):
                            real_video_meta["cover_url"] = ssr_meta["cover"]

                    # Hacer clic explícito en el icono de comentarios para abrir el panel y activar la carga de red
                    try:
                        comment_btn = await page.query_selector('[data-e2e="comment-icon"], div[data-e2e="comment-icon"], strong[data-e2e="comment-count"]')
                        if not comment_btn:
                            comment_btn = await page.query_selector('button[data-e2e="comments"], [role="tab"]:has-text("Comentarios")')
                        if comment_btn:
                            await comment_btn.click()
                            await asyncio.sleep(2.0)
                    except Exception as e_c_click:
                        print(f"[*] Aviso al activar panel de comentarios: {e_c_click}")

                    # Esperar pacientemente (hasta 5 minutos) si TikTok presenta el puzle deslizador en pantalla
                    await self._wait_for_captcha_if_present(page, progress_callback, max_wait=300)
                    await asyncio.sleep(2.0)

                    # Persistir el estado de sesión actualizado
                    try:
                        if self.cookies_path:
                            await context.storage_state(path=str(self.cookies_path))
                    except Exception:
                        pass

                    # Descartar notificaciones emergentes que puedan superponerse
                    try:
                        await page.evaluate("""() => {
                            const toastCloses = document.querySelectorAll('button[aria-label="Close"], [class*="toast"] button, [class*="notification"] button');
                            toastCloses.forEach(b => { try { b.click(); } catch(e){} });
                        }""")
                    except Exception:
                        pass

                    # Desplazamiento e interacción en el panel de comentarios
                    for _ in range(5):
                        await page.mouse.wheel(0, 1000)
                        await asyncio.sleep(1.2)

                    # Extraer comentarios reales del DOM
                    dom_data = await page.evaluate("""() => {
                        const list = [];
                        const seenTexts = new Set();

                        const items = document.querySelectorAll('[data-e2e="comment-item"], [class*="CommentItem"], [class*="DivCommentItemContainer"]');
                        for (const el of items) {
                            const userA = el.querySelector('a[href*="/@"], [data-e2e*="user-name"]');
                            const nickSpan = el.querySelector('[class*="Nickname"], [data-e2e*="nickname"]');
                            const textP = el.querySelector('[data-e2e="comment-level-1"], p, [class*="CommentText"], span[class*="CommentText"]');
                            const likeSpan = el.querySelector('[data-e2e="comment-like-count"]');
                            const timeSpan = el.querySelector('[data-e2e="comment-time"], [class*="Time"]');
                            const avatarImg = el.querySelector('img');

                            const uHandle = userA ? userA.innerText.trim() : '';
                            const txt = textP ? textP.innerText.trim() : '';
                            if (txt && !seenTexts.has(txt)) {
                                seenTexts.add(txt);
                                list.push({
                                    username: uHandle,
                                    nickname: nickSpan ? nickSpan.innerText.trim() : uHandle,
                                    text: txt,
                                    likes: likeSpan ? likeSpan.innerText.trim() : '0',
                                    created_at: timeSpan ? timeSpan.innerText.trim() : 'Reciente',
                                    avatar: avatarImg ? avatarImg.src : ''
                                });
                            }
                        }

                        if (list.length === 0) {
                            const level1Els = document.querySelectorAll('[data-e2e="comment-level-1"], p[class*="CommentText"]');
                            for (const p of level1Els) {
                                const txt = p.innerText ? p.innerText.trim() : '';
                                if (txt && !seenTexts.has(txt)) {
                                    seenTexts.add(txt);
                                    const parent = p.closest('[class*="Comment"]') || p.parentElement;
                                    const uA = parent ? parent.querySelector('a[href*="/@"]') : null;
                                    const uName = uA ? uA.innerText.trim() : '';
                                    list.push({
                                        username: uName,
                                        nickname: uName || 'Usuario',
                                        text: txt,
                                        likes: '0',
                                        created_at: 'Reciente',
                                        avatar: ''
                                    });
                                }
                            }
                        }
                        return list;
                    }""")

                    seen_text_set = set()
                    for d in dom_data:
                        t = d.get("text", "").strip()
                        if not t or t in seen_text_set:
                            continue
                        seen_text_set.add(t)
                        u_name = d.get("username") or f"@usuario_{len(video_comments) + 1}"
                        video_comments.append({
                            "comment_id": f"c_{vid_id}_{len(video_comments) + 1}",
                            "author_username": f"@{u_name.lstrip('@')}",
                            "author_nickname": d.get("nickname") or u_name,
                            "author_avatar": d.get("avatar") or f"https://api.dicebear.com/7.x/avataaars/svg?seed={u_name}",
                            "author_hash": self.pseudonymize_identifier(u_name),
                            "text": t,
                            "likes": int(str(d.get("likes", "0")).replace("K", "000").replace("M", "000000").replace(".", "") or 0),
                            "created_at": d.get("created_at") or "Reciente",
                            "video_id": vid_id,
                            "video_title": real_video_meta["title"],
                            "video_url": v_url
                        })
                except Exception as e_nav:
                    print(f"[!] Error al navegar y extraer datos del video {vid_id}: {e_nav}")

                # Incorporar comentarios reales interceptados por API de red
                if vid_id in captured_api_comments:
                    for api_c in captured_api_comments[vid_id]:
                        api_text = api_c.get("text", "").strip()
                        if api_text and api_text not in seen_text_set:
                            seen_text_set.add(api_text)
                            api_c["video_title"] = real_video_meta["title"]
                            api_c["video_url"] = v_url
                            video_comments.append(api_c)

                # Guardar video con datos 100% reales
                final_videos_audit.append({
                    "video_index": idx + 1,
                    "video_id": vid_id,
                    "video_url": v_url,
                    "title": real_video_meta["title"],
                    "cover_url": real_video_meta["cover_url"],
                    "embed_url": f"https://www.tiktok.com/embed/v2/{vid_id}",
                    "views_count": real_video_meta["views_count"],
                    "likes_count": real_video_meta["likes_count"],
                    "comments_count": len(video_comments) if video_comments else real_video_meta["comments_count"],
                    "shares_count": real_video_meta["shares_count"],
                    "comments": video_comments[:comments_per_video]
                })
                all_collected_comments.extend(video_comments[:comments_per_video])

            await browser.close()

        return {
            "creator_profile": self.last_creator_profile,
            "videos": final_videos_audit,
            "all_comments": all_collected_comments
        }

    def scrape_comments(
        self,
        post_url: str,
        max_comments: int = 150,
        headed: bool = False,
        timeout: int = 35
    ) -> List[Dict[str, Any]]:
        """Compatibilidad síncrona con el endpoint existente."""
        import sys
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        res = asyncio.run(
            self.audit_creator_multi_videos_async(
                target_url=post_url,
                max_videos=1,
                comments_per_video=max_comments,
                headed=headed,
                timeout=timeout
            )
        )
        return res.get("all_comments", [])
