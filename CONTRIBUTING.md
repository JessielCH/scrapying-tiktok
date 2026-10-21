# Contributing to TikTok Scraper & Session Cookie Manager

First off, thank you for considering contributing to this project! It's people like you that make open source tools great.

---

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please report unacceptable behavior to the project maintainers.

---

## How Can I Contribute?

### Reporting Bugs
Before creating bug reports, please check existing issues to avoid duplicates. When filing a bug report, include:
- A clear, descriptive title.
- Steps to reproduce the issue.
- TikTok response status or error codes (e.g., HTTP 403, 10202, captcha trigger).
- Operating system and Python version.
- **Do not share personal cookies or credentials in issue descriptions or logs.**

### Suggesting Enhancements
Feature requests are welcome! Please specify:
- The problem you are trying to solve.
- Your proposed solution or API design.
- Any relevant TikTok endpoint or network trace details.

### Pull Requests
1. **Fork** the repository and create your branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Install** dependencies and test your changes in an isolated environment.
3. Follow the project's coding standards:
   - Follow **PEP 8** style guidelines.
   - Use type annotations wherever applicable.
   - Write clear docstrings in English.
4. Commit your changes with meaningful commit messages following [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat: add comment pagination support`
   - `fix: handle expired ttwid cookie gracefully`
   - `docs: update anti-detect reference guide`
5. Push to your fork and submit a **Pull Request** against `main`.

---

## Development Setup

```bash
git clone https://github.com/<your-username>/scrap-tiktok.git
cd scrap-tiktok
python -m venv .venv
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
pip install -r requirements.txt
playwright install chromium
```

---

## Security & Privacy Guidelines

- Never commit real user cookies (`sessionid`), tokens, or credentials into the repository.
- Ensure that tests and sample data use sanitized or mock identifiers.
