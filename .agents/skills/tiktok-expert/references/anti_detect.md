# TikTok Anti-Detection & Evasion Guide

TikTok uses sophisticated anti-bot defenses managed by **Akamai Bot Manager** combined with ByteDance proprietary heuristics.

---

## 1. Layers of Detection

### Tier 1: TLS / TCP Fingerprinting (JA3 / JA4)
- **The Issue:** When Python libraries such as `requests`, `urllib`, or `aiohttp` initiate an HTTPS connection, the TLS `ClientHello` contains specific cipher suites, extensions, and elliptic curve formats that differ sharply from legitimate commercial browsers.
- **Detection:** Akamai evaluates the **JA3/JA4** hash. Non-browser client handshakes are immediately blocked with **HTTP 403 Forbidden** or hard captchas.
- **Solution:**
  - Use **`curl_cffi`**, which uses a modified libcurl engine able to mirror Chrome (`chrome120`, `chrome124`) TLS handshakes byte-by-byte.
  - Or use a real browser engine driven by **Playwright**.

---

### Tier 2: Browser Fingerprinting
When driving an automated browser, TikTok scripts inspect client-side properties:

1. **`navigator.webdriver`:** If set to `true`, the session is discarded immediately.
   - *Bypass:* Inject `Object.defineProperty(navigator, 'webdriver', {get: () => undefined})` prior to document evaluation.
2. **WebGL & Canvas:** Extracting GPU rendering vendor signatures (`WEBGL_debug_renderer_info`).
3. **`navigator.plugins` & `navigator.languages`:** Verifying that plugins and locale arrays reflect legitimate desktop configurations.
4. **Chrome Runtime:** Checking for `window.chrome.runtime` and associated methods.

---

### Tier 3: Cryptographic Signatures (`X-Bogus`, `_signature`, `msToken`)
- Requests to TikTok's internal web APIs (`/api/...`) enforce dynamic query signatures calculated via obfuscated WebAssembly.
- Requests lacking `X-Bogus` or containing mismatched URL hashes yield errors or empty arrays.
- **Bypass Approaches:**
  - **Network Interception in Playwright:** Let TikTok's legitimate web scripts calculate signatures and capture the raw response payload with `page.on('response', ...)`.
  - **Scraping via SSR Hydration Data:** Avoid calling dynamic APIs altogether by reading data from the server-rendered HTML `<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__">`, which requires zero `X-Bogus` signing.

---

## 2. Playwright Stealth Configuration

```python
from playwright.async_api import async_playwright

async def get_stealth_browser():
    p = await async_playwright().start()
    browser = await p.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--window-size=1920,1080",
        ]
    )
    context = await browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        locale="en-US",
        timezone_id="America/New_York"
    )
    
    # Inject baseline evasion
    await context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        window.chrome = { runtime: {} };
    """)
    return p, browser, context
```

---

## 3. Behavioral Emulation & Delays
- **Natural Scrolling:** Scroll with variable step intervals (`window.scrollBy(0, Math.floor(Math.random() * 400 + 200))`).
- **Sleep Intervals:** Introduce randomized delays (1.5s to 4.0s) between actions.
- **Residential Proxies:** When collecting large data volumes (>500 items/day), route traffic through rotating residential or 4G/5G mobile proxies.
