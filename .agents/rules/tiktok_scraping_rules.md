# Engineering Rules & Directives for TikTok Scraping

These engineering rules must be strictly adhered to across all tools, scripts, and modules developed in this workspace.

---

## 1. Anti-Bot & TLS Evasion Rules (Anti-Detect)
1. **Ban on TLS Fingerprint-Leaking Libraries:**
   - Standard HTTP libraries such as `requests`, `urllib`, or plain `aiohttp` must never make direct requests to `tiktok.com`.
   - Akamai Bot Manager intercepts connections by inspecting the TLS `ClientHello` (ciphers, extensions, elliptic curves).
   - **Mandatory standard:** Use `curl_cffi.requests` configured with `impersonate="chrome120"` (or `chrome124`), or use a stealth Playwright browser.

2. **Required HTTP Request Headers:**
   - `User-Agent`: Must precisely match the browser version being impersonated.
   - `Referer`: Always send `https://www.tiktok.com/`.
   - `sec-ch-ua`, `sec-ch-ua-mobile`, `sec-ch-ua-platform`: Must match the target OS and browser version.
   - `Accept-Language`: Set to `en-US,en;q=0.9` or relevant target regional locale.

3. **Playwright Stealth Configuration:**
   - Mask `navigator.webdriver`.
   - Mock `navigator.plugins`, `navigator.languages`, and `window.chrome.runtime`.
   - Use realistic screen resolutions (e.g., 1920x1080) and human-like cursor/scroll movements.

---

## 2. Cookie Extraction & Persistence Rules
1. **The Vital `ttwid` (TikTok Web ID) Cookie:**
   - Without `ttwid`, TikTok flags requests as untrusted or uninitialized, returning empty JSON arrays or `status_code: 10202`.
   - When no prior session exists, scripts must bootstrap `ttwid` by requesting `https://www.tiktok.com/` before calling internal API endpoints.

2. **Authenticated Sessions (`sessionid` and `sessionid_ss`):**
   - For restricted content (private accounts, age-gated media, following feeds), persistent authenticated cookies are required.
   - Store sessions in `data/` supporting:
     - **JSON** format (Playwright `storage_state`).
     - **Netscape** format (`cookies.txt` compatible with `yt-dlp` and `curl`).

3. **Renewal & Expiration:**
   - Detect HTTP 403, redirection to login, or JSON response codes `status_code != 0` as indicators of expired or challenged sessions.
   - Implement exponential backoff and jitter for retries.

---

## 3. Data Extraction Strategy
1. **Priority 1: SSR Hydration Data:**
   - On video (`/@user/video/ID`) or profile (`/@user`) URLs, TikTok injects initial state into:
     ```html
     <script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">
     ```
   - This JSON contains creator details (`author`, `stats`, `secUid`), video streams (`playAddr`, `downloadAddr`), audio metadata (`music`), and metrics (`diggCount`, `playCount`).
   - This approach is 10x faster than full JavaScript browser rendering and avoids `X-Bogus` signing.

2. **Priority 2: Dynamic Feed & Comment Pagination:**
   - For long lists (100+ videos or thousands of comments), use Playwright listening to network events (`page.on('response', ...)`) matching `/api/post/item_list/` or `/api/comment/list/`.

3. **Watermark-Free Video Downloads:**
   - Use the direct CDN link obtained from `playAddr`, or integrate `yt-dlp` with the exported cookies (`--cookies data/cookies.txt`).
