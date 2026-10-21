# TikTok Scraper & Session Cookie Manager

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/playwright-stealth-green.svg)](https://playwright.dev/)
[![TLS Impersonation](https://img.shields.io/badge/TLS-curl__cffi-orange.svg)](https://github.com/yifeikong/curl_cffi)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A high-performance, stealthy scraper and session cookie management toolkit for **TikTok**. Built to bypass Akamai Bot Manager, TLS/JA3 fingerprinting, and dynamic signing barriers with native support for both guest and authenticated sessions.

---

## 🌟 Key Features

- **🛡️ Anti-Detect & TLS Evasion:** Uses `curl_cffi` to impersonate real Chrome 120/124 TLS handshakes (JA3/JA4 fingerprint matching), preventing immediate `HTTP 403 Forbidden` responses.
- **🍪 Full Cookie & Session Management:**
  - **Guest Mode (`--mode guest`):** Headless extraction of required guest cookies (`ttwid`, `msToken`).
  - **Interactive Login (`--mode login`):** Headed Chromium browser supporting QR code or manual login to capture full authentication sessions (`sessionid`, `sessionid_ss`).
  - **Dual Export Formats:** Exports to both JSON (Playwright `storage_state`) and standard Netscape format (`cookies.txt` compatible with `yt-dlp` and `curl`).
- **⚡ Ultra-Fast SSR Hydration Parsing:** Extracts structured data directly from the `<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__">` tag, avoiding complex JS execution and dynamic API signing (`X-Bogus`).
- **🎥 Watermark-Free Video Downloads:** Directly fetches the clean CDN stream (`playAddr` / `downloadAddr`) or pairs seamlessly with `yt-dlp`.
- **🤖 Built-in AI Agent Capabilities:** Bundles native `.agents/` rules, skills, and runbooks compatible with Antigravity / Agentic IDEs.

---

## 📁 Repository Structure

```text
scrap-tiktok/
├── src/                                                # Core modular source package
│   ├── __init__.py                                     # Package exports
│   ├── cookie_manager.py                               # Playwright session & cookie manager
│   ├── scraper.py                                      # SSR hydration parser & video streamer
│   ├── user_analyzer.py                                # User profile & engagement metrics analyzer
│   ├── anti_detect.py                                  # Browser headers & stealth scripts
│   └── utils.py                                        # Netscape/JSON serializers & loaders
├── data/                                               # Session & media output (gitignored)
│   ├── .gitkeep
│   └── downloads/
│       └── .gitkeep
├── main.py                                             # Unified CLI entry point
├── requirements.txt                                    # Python dependencies
├── .agent                                              # Agent persona & quick references
├── AGENTS.md                                           # Hierarchical workspace agent rules
├── .agents/
│   ├── rules/
│   │   └── tiktok_scraping_rules.md                    # Engineering rules (Anti-detect & session lifecycles)
│   └── skills/
│       └── tiktok-expert/
│           ├── SKILL.md                                # Autonomous agent workflow & runbooks
│           └── references/                             # Anti-detect, cookies, and endpoint guides
├── CONTRIBUTING.md                                     # Contribution guidelines
├── CODE_OF_CONDUCT.md                                 # Code of Conduct
├── LICENSE                                             # MIT License
├── README.md                                           # Project documentation (this file)
└── SECURITY.md                                         # Security disclosure policy
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10 or higher
- Git

### 2. Installation

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/JessielCH/scrapying-tiktok.git
cd scrapying-tiktok

# Create and activate a virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser binaries
playwright install chromium
```

---

## 📖 Usage Guide

### 🚀 Interactive Console Mode (Recommended)
Simply launch `main.py` without arguments or with `interactive` to enter the interactive console:
```bash
python main.py
# or: python main.py interactive
```
This interactive prompt guides you through:
- Entering any TikTok username or profile link (`@username`).
- Selecting how many posts (videos & carousels) to analyze (default: 10).
- Toggling visible browser mode (`headed`) if you need to solve captcha verification puzzles interactively.
- Extracting / refreshing cookies (Guest or Login QR).
- Downloading media files (video `.mp4` or all carousel `.jpg` slides).

---

### 1. Extracting Cookies & Session

TikTok requires valid cookies (especially `ttwid`) for most operations. Use the provided cookie extractor:

#### A. Guest Mode (Automated, Headless)
Extracts public guest cookies without requiring user interaction:
```bash
python main.py extract-cookies --mode guest
```
Output files:
- `data/cookies.json` (Playwright state format)
- `data/cookies.txt` (Netscape HTTP format)

#### B. Authenticated Login Mode (Interactive)
Opens a visible browser for QR code scanning or manual login:
```bash
python main.py extract-cookies --mode login
```
*Once logged in, it automatically captures `sessionid` and persists your session.*

---

### 2. Scraping Posts (Videos & Carousels)

Use the fast SSR rehydration scraper to extract video or photo carousel details, creator info, metrics, and direct media links:

```bash
python main.py scrape "https://www.tiktok.com/@username/video/1234567890123456789"
```

To automatically download the video without watermarks (or download all carousel image slides):
```bash
python main.py scrape "https://www.tiktok.com/@username/video/1234567890123456789" --download
```

---

### 3. User Profile & Recent Posts Analysis (Videos & Carousels)

Extract a TikTok user's complete profile information (username, display name, biography, verified badge, following count, follower count, total likes received, total video count) and calculate **numerical engagement metrics across their latest posts** (supporting both standard videos and photo carousels):

```bash
# Analyze user profile and last 10 posts (videos + carousels)
python main.py analyze-user @username

# Analyze with custom post limit
python main.py analyze-user @username --max-videos 10

# Pass authenticated session cookies
python main.py analyze-user @username --cookies data/cookies.json

# Run headed (if captcha verification slider is encountered)
python main.py analyze-user @username --headed
```

Generated reports are displayed cleanly in the console and exported to structured JSON format at `data/analysis_<username>.json`.

---

### 4. Python API Integration

You can also import the modules directly in your own Python projects:

```python
from src.scraper import TikTokScraper
from src.cookie_manager import TikTokCookieManager

# Extract guest cookies
manager = TikTokCookieManager(output_dir="data")
manager.extract_guest_cookies()

# Scrape video metadata
scraper = TikTokScraper(cookies_path="data/cookies.json")
metadata = scraper.get_metadata("https://www.tiktok.com/@username/video/1234567890123456789")
print(metadata)
```

---

### 5. Downloading with `yt-dlp`

Use the exported Netscape cookie file to download high-resolution videos using `yt-dlp`:

```bash
yt-dlp --cookies data/cookies.txt "https://www.tiktok.com/@username/video/1234567890123456789" -o "data/downloads/%(id)s.%(ext)s"
```

---

## 🛡️ Anti-Detect & Stealth Details

TikTok's Akamai Bot Manager inspects the TLS `ClientHello` packet. Conventional HTTP libraries like Python `requests` or `urllib` send signatures that are instantly fingerprinted as bots.

| Technique | Conventional Scraping | This Project |
| :--- | :--- | :--- |
| **TLS Handshake (JA3/JA4)** | Python default (Blocked with 403) | Impersonates Chrome 120+ via `curl_cffi` |
| **Browser Context** | `navigator.webdriver = true` | Evasion via `playwright-stealth` scripts |
| **Session Tracking** | Missing `ttwid` (Status 10202) | Automated guest & authenticated cookie management |
| **Payload Extraction** | Heavy dynamic API calls | SSR Hydration (`__UNIVERSAL_DATA_FOR_REHYDRATION__`) |

For comprehensive technical analysis, consult [.agents/skills/tiktok-expert/references/anti_detect.md](.agents/skills/tiktok-expert/references/anti_detect.md).

---

## 🤝 Contributing

Contributions are warmly welcomed! Please read [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before opening a pull request or submitting an issue.

---

## ⚖️ Legal Disclaimer

This repository is for educational, research, and data archival purposes only. Scraping must comply with relevant terms of service, platform policies, and applicable copyright laws. The authors and contributors assume no liability for misuse of this tool.

---

## 📄 License

Distributed under the [MIT License](LICENSE).
