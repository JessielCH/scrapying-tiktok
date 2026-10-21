---
name: tiktok-expert
description: >-
  Expert in TikTok web scraping, frontend and API reverse engineering, session cookie extraction and persistence (Playwright, CDP, Netscape, and JSON), Akamai anti-bot and TLS/JA3 fingerprint evasion with curl_cffi, SSR metadata harvesting, and watermark-free media downloads. Use whenever scraping TikTok, managing session cookies, or automating browser tasks on the platform.
---

# TikTok Scraping & Cookie Extraction Skill

This skill provides step-by-step procedures, technical specifications, and operational workflows for robust TikTok data extraction, session lifecycle management, and anti-bot defense evasion.

## 🎯 Core Engineering Directives
- **Zero External APIs & Zero Pre-Made Wrappers:**
  - Strictly NO reliance on official TikTok Developer APIs, OAuth tokens, or third-party scraping SaaS (Apify, RapidAPI, etc.).
  - Strictly NO pre-made TikTok library wrappers (e.g. `TikTokApi`, `pyktok`).
  - Everything is built using basic, fundamental web scraping: direct Playwright browser sessions, direct BeautifulSoup HTML hydration extraction (`__UNIVERSAL_DATA_FOR_REHYDRATION__`), and direct `curl_cffi` HTTP requests.
- **User-Led Testing:**
  - The user executes all live tests. The AI agent must never execute scraping commands against TikTok accounts unprompted.

---

## 📚 Quick Reference Documentation
- **Cookies & Session Guide:** [references/cookies_guide.md](./references/cookies_guide.md)
  *Structure of `ttwid`, `sessionid`, `msToken`, Netscape vs JSON formats.*
- **Anti-Detect & Evasion Guide:** [references/anti_detect.md](./references/anti_detect.md)
  *Bypassing Akamai Bot Manager, TLS JA3/JA4, stealth scripts, and residential proxies.*
- **TikTok API Catalog:** [references/api_endpoints.md](./references/api_endpoints.md)
  *Endpoints `/api/post/item_list/`, `/api/comment/list/`, SSR payload structure.*

---

## 🛠️ Workflows & Runbooks

### Workflow 1: Session Cookie Extraction
To perform authenticated scraping or bypass guest limitations, use one of two extraction modes:

1. **Guest Mode (Automated, Headless):**
   - Retrieves fundamental public cookies (`ttwid`, `msToken`).
   - Runs headlessly without user intervention, generating `data/cookies.json` and `data/cookies.txt`.
   - Command: `python main.py extract-cookies --mode guest`

2. **Authenticated Login Mode (Interactive, Headed):**
   - Opens a real Chromium browser with Playwright for user login (via QR code or credentials).
   - Captures full session state (`sessionid`, `sessionid_ss`, `tt_chain_token`, `storage_state`).
   - Command: `python main.py extract-cookies --mode login`

---

### Workflow 2: Ultra-Fast Video & Profile Scraping (SSR Hydration)
TikTok renders initial state on the server and embeds complete data in the HTML:
```html
<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">
```

**Steps:**
1. Send a GET request using `curl_cffi` impersonating Chrome:
   ```python
   from src.scraper import TikTokScraper
   scraper = TikTokScraper(cookies_path="data/cookies.json")
   metadata = scraper.get_metadata(url)
   ```
2. Parse HTML and locate `#__UNIVERSAL_DATA_FOR_REHYDRATION__`.
3. Decode JSON. Key data paths:
   - `__DEFAULT_SCOPE__.__DEFAULT_SCOPE__['webapp.video-detail']['itemInfo']['itemStruct']` for videos.
   - `__DEFAULT_SCOPE__.__DEFAULT_SCOPE__['webapp.user-detail']['userInfo']` for user profiles.
4. Extract direct CDN watermark-free video URL from `video['playAddr']` or `video['downloadAddr']`.
5. Run via CLI:
   ```bash
   python main.py scrape "https://www.tiktok.com/@username/video/1234567890" --download
   ```

---

### Workflow 3: Dynamic User Feed & Comment Pagination
To extract full video lists or thousands of comments:

1. Launch a Playwright instance with stealth options.
2. Load persisted cookies (`context = browser.new_context(storage_state="data/cookies.json")`).
3. Intercept backend responses using a network listener:
   ```python
   async def handle_response(response):
       if "/api/post/item_list/" in response.url or "/api/comment/list/" in response.url:
           data = await response.json()
           # process items
   page.on("response", handle_response)
   ```
4. Emulate smooth scrolling with randomized pauses (1.5s - 3.5s) to trigger infinite loading.

---

### Workflow 4: High-Quality Video Downloads with `yt-dlp`
Utilize `yt-dlp` alongside the exported Netscape cookie file:
```bash
yt-dlp --cookies data/cookies.txt "https://www.tiktok.com/@username/video/1234567890" -o "data/downloads/%(id)s.%(ext)s"
```

---

## 🚨 Troubleshooting & Error Codes

| Symptom / Error | Root Cause | Resolution |
| :--- | :--- | :--- |
| **HTTP 403 Forbidden** | Akamai detected an anomalous TLS fingerprint (Python `requests` JA3). | Switch from `requests` to `curl_cffi` with `impersonate="chrome120"` or use Playwright. |
| **Empty response / `status_code: 10202`** | Missing `ttwid` cookie. | Bootstrap cookies by visiting the homepage first, then pass `ttwid` in subsequent requests. |
| **Captcha Slider / Puzzle Challenge** | High request rate or flagged IP. | Increase delays (2s - 5s), rotate residential IPs, or solve interactively with Playwright `headless=False`. |
| **Video URL expires or returns 403** | CDN URLs (`playAddr`) have short TTLs and require matching headers. | Stream-download the video immediately using the same `User-Agent` and `Referer`. |
