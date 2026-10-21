import os
import sys
import json
import time
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    from playwright.async_api import async_playwright, BrowserContext
except ImportError:
    async_playwright = None

from .utils import ensure_output_dir, export_to_netscape_format
from .anti_detect import DEFAULT_USER_AGENT, get_stealth_browser_args, get_stealth_init_script


class TikTokCookieManager:
    """
    Handles session and cookie extraction for TikTok.
    Supports headless guest bootstrap and headed interactive QR/credentials login.
    """

    def __init__(self, output_dir: str = "data"):
        self.output_dir = Path(output_dir)
        ensure_output_dir(self.output_dir)

    def _check_playwright(self):
        if async_playwright is None:
            raise RuntimeError(
                "Playwright is not installed. Please install it using:\n"
                "  pip install playwright && playwright install chromium"
            )

    async def extract_guest_cookies_async(self) -> Dict[str, Any]:
        """
        Launches a headless browser to obtain guest cookies (ttwid, msToken).
        Saves data to cookies.json and cookies.txt.
        """
        self._check_playwright()
        print("[*] Iniciando extracción en MODO INVITADO (segundo plano)...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=get_stealth_browser_args()
            )
            context = await browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent=DEFAULT_USER_AGENT
            )
            await context.add_init_script(get_stealth_init_script())
            page = await context.new_page()

            print("[*] Navegando a https://www.tiktok.com/ ...")
            try:
                await page.goto("https://www.tiktok.com/", wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(4)
            except Exception as e:
                print(f"[!] Aviso durante la navegación: {e}")

            cookies = await context.cookies()
            storage_state = await context.storage_state()

            # Guardar JSON de Playwright
            json_path = self.output_dir / "cookies.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(storage_state, f, indent=2)
            print(f"[OK] Estado de sesion guardado: {json_path}")

            # Guardar formato Netscape
            txt_path = self.output_dir / "cookies.txt"
            export_to_netscape_format(cookies, txt_path)
            print(f"[OK] Cookies en formato Netscape guardadas: {txt_path}")

            cookie_names = [c["name"] for c in cookies]
            print(f"[INFO] Total de cookies obtenidas: {len(cookies)} (ttwid: {'OK' if 'ttwid' in cookie_names else 'NO'})")

            await browser.close()
            return storage_state

    async def extract_login_cookies_async(self, timeout: int = 300) -> Dict[str, Any]:
        """
        Abre una ventana de navegador interactiva para inicio de sesión con QR o credenciales.
        Detecta la cookie de autenticación (sessionid) y persiste el estado completo.
        """
        self._check_playwright()
        print("[*] Iniciando extracción en MODO AUTENTICADO (interactivo con ventana)...")
        print("[*] Se abrirá una ventana de navegador. Por favor inicia sesión con tu cuenta de TikTok.")

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                args=["--disable-blink-features=AutomationControlled", "--start-maximized"]
            )
            context = await browser.new_context(
                no_viewport=True,
                user_agent=DEFAULT_USER_AGENT
            )
            await context.add_init_script(get_stealth_init_script())
            page = await context.new_page()

            await page.goto("https://www.tiktok.com/login", wait_until="domcontentloaded")
            print("\n" + "=" * 60)
            print(">> Inicia sesión con código QR o credenciales en el navegador.")
            print(">> Esperando detección de la cookie 'sessionid'...")
            print("=" * 60 + "\n")

            start_time = time.time()
            logged_in = False

            while time.time() - start_time < timeout:
                try:
                    if page.is_closed():
                        print("[*] La ventana del navegador fue cerrada por el usuario.")
                        break
                    cookies = await context.cookies()
                    names = [c["name"] for c in cookies]
                    if "sessionid" in names or "sessionid_ss" in names:
                        print("\n[OK] Cookie de sesion 'sessionid' capturada exitosamente.")
                        logged_in = True
                        await asyncio.sleep(2)
                        break
                except Exception:
                    break
                await asyncio.sleep(2)

            if not logged_in:
                print("[!] Tiempo límite alcanzado o ventana cerrada. Exportando cookies capturadas...")

            cookies = await context.cookies()
            storage_state = await context.storage_state()

            # Guardar JSON de Playwright
            json_path = self.output_dir / "cookies.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(storage_state, f, indent=2)
            print(f"[OK] Estado de sesion guardado: {json_path}")

            # Guardar formato Netscape
            txt_path = self.output_dir / "cookies.txt"
            export_to_netscape_format(cookies, txt_path)
            print(f"[OK] Cookies en formato Netscape guardadas: {txt_path}")

            await browser.close()
            return storage_state

    def has_valid_cookies(self) -> bool:
        """
        Verifica si existe el archivo de cookies y si contiene cookies validas.
        """
        json_path = self.output_dir / "cookies.json"
        if not json_path.exists():
            return False
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            cookies = data.get("cookies", [])
            if not cookies:
                return False
            names = {c.get("name") for c in cookies}
            return "sessionid" in names or "sessionid_ss" in names or "ttwid" in names
        except Exception:
            return False

    def is_authenticated(self) -> bool:
        """Verifica si la sesion guardada cuenta con autenticacion de usuario (sessionid)."""
        json_path = self.output_dir / "cookies.json"
        if not json_path.exists():
            return False
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            names = {c.get("name") for c in data.get("cookies", [])}
            return "sessionid" in names or "sessionid_ss" in names
        except Exception:
            return False

    def ensure_cookies(self, prefer_login: bool = False) -> Path:
        """
        Garantiza de forma obligatoria que existan cookies validas antes de continuar.
        Si no existen, ejecuta la obtencion correspondiente para evitar el bloqueo HTTP 403.
        """
        json_path = self.output_dir / "cookies.json"
        if self.has_valid_cookies() and not prefer_login:
            return json_path

        print("\n" + "=" * 65)
        print("[OBLIGATORIO] VALIDACION DE SESION Y COOKIES")
        print("=" * 65)
        print("TikTok deniega el acceso (HTTP 403 / Bloqueo) a peticiones sin cookies.")
        print("Es obligatorio inicializar una sesion con cookies para continuar.")
        print("=" * 65 + "\n")

        if prefer_login:
            print("[*] Iniciando modo login para capturar sesion autenticada...")
            self.extract_login_cookies()
        else:
            print("[*] Obteniendo cookies iniciales obligatorias (ttwid)...")
            try:
                self.extract_guest_cookies()
            except Exception as e:
                print(f"[!] Error en modo invitado ({e}). Se intentara modo login con ventana.")
                self.extract_login_cookies()

            if not self.has_valid_cookies():
                print("\n[!] Las cookies basicas fueron bloqueadas por el firewall de TikTok.")
                print("[*] Abriendo ventana de navegador para inicio de sesion (QR o credenciales)...")
                self.extract_login_cookies()

        if not self.has_valid_cookies():
            raise RuntimeError(
                "No fue posible obtener cookies validas. "
                "TikTok exige iniciar sesion para procesar consultas sin denegar el acceso."
            )

        print("[OK] Sesion validada correctamente. Procediendo con la operacion.\n")
        return json_path

    def extract_guest_cookies(self) -> Dict[str, Any]:
        """Synchronous wrapper for guest cookie extraction."""
        return asyncio.run(self.extract_guest_cookies_async())

    def extract_login_cookies(self, timeout: int = 300) -> Dict[str, Any]:
        """Synchronous wrapper for interactive login extraction."""
        return asyncio.run(self.extract_login_cookies_async(timeout=timeout))
