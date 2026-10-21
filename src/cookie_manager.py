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
        print("[*] Starting GUEST extraction (Headless)...")
        
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

            print("[*] Navigating to https://www.tiktok.com/ ...")
            try:
                await page.goto("https://www.tiktok.com/", wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(4)
            except Exception as e:
                print(f"[!] Notice during navigation: {e}")

            cookies = await context.cookies()
            storage_state = await context.storage_state()

            # Save Playwright JSON
            json_path = self.output_dir / "cookies.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(storage_state, f, indent=2)
            print(f"[✓] Session saved: {json_path}")

            # Save Netscape format
            txt_path = self.output_dir / "cookies.txt"
            export_to_netscape_format(cookies, txt_path)
            print(f"[✓] Netscape cookies saved: {txt_path}")

            cookie_names = [c["name"] for c in cookies]
            print(f"[i] Total cookies: {len(cookies)} (ttwid: {'✓' if 'ttwid' in cookie_names else '✗'})")

            await browser.close()
            return storage_state

    async def extract_login_cookies_async(self, timeout: int = 300) -> Dict[str, Any]:
        """
        Launches an interactive browser window for QR code or credentials login.
        Detects authenticated cookies (sessionid) and saves full state.
        """
        self._check_playwright()
        print("[*] Starting AUTHENTICATED extraction (Interactive)...")
        print("[*] A browser window will open. Please log in with your TikTok account.")

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
            print(">> Log in via QR code or credentials inside the browser window.")
            print(">> Waiting for 'sessionid' cookie...")
            print("=" * 60 + "\n")

            start_time = time.time()
            logged_in = False

            while time.time() - start_time < timeout:
                try:
                    if page.is_closed():
                        print("[*] Browser page was closed by user.")
                        break
                    cookies = await context.cookies()
                    names = [c["name"] for c in cookies]
                    if "sessionid" in names or "sessionid_ss" in names:
                        print("\n[🎉] Authenticated session cookie 'sessionid' captured!")
                        logged_in = True
                        await asyncio.sleep(2)
                        break
                except Exception:
                    break
                await asyncio.sleep(2)

            if not logged_in:
                print("[!] Timeout reached or browser closed. Exporting available cookies...")

            cookies = await context.cookies()
            storage_state = await context.storage_state()

            # Save Playwright JSON
            json_path = self.output_dir / "cookies.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(storage_state, f, indent=2)
            print(f"[✓] Session state saved: {json_path}")

            # Save Netscape format
            txt_path = self.output_dir / "cookies.txt"
            export_to_netscape_format(cookies, txt_path)
            print(f"[✓] Netscape cookies saved: {txt_path}")

            await browser.close()
            return storage_state

    def extract_guest_cookies(self) -> Dict[str, Any]:
        """Synchronous wrapper for guest cookie extraction."""
        return asyncio.run(self.extract_guest_cookies_async())

    def extract_login_cookies(self, timeout: int = 300) -> Dict[str, Any]:
        """Synchronous wrapper for interactive login extraction."""
        return asyncio.run(self.extract_login_cookies_async(timeout=timeout))
