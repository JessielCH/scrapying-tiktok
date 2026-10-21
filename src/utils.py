import json
import time
from pathlib import Path
from typing import List, Dict, Any


def ensure_output_dir(dir_path: Path) -> Path:
    """Ensures directory exists and returns Path object."""
    dir_path = Path(dir_path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def export_to_netscape_format(cookies: List[Dict[str, Any]], output_file: Path):
    """
    Exports a list of cookie dictionaries to the standard Netscape / curl format.
    Compatible with yt-dlp, curl, and requests.
    """
    output_file = Path(output_file)
    ensure_output_dir(output_file.parent)

    lines = [
        "# Netscape HTTP Cookie File",
        "# https://curl.se/docs/http-cookies.html",
        "# Generated automatically by TikTok Cookie Manager",
        ""
    ]
    
    current_time = int(time.time())
    one_year_later = current_time + (365 * 24 * 3600)

    for c in cookies:
        domain = c.get("domain", ".tiktok.com")
        flag = "TRUE" if domain.startswith(".") else "FALSE"
        path = c.get("path", "/")
        secure = "TRUE" if c.get("secure", False) else "FALSE"
        
        expires = c.get("expires", -1)
        if expires is None or expires <= 0:
            expires = one_year_later
        else:
            expires = int(expires)
            
        name = c.get("name", "")
        value = c.get("value", "")
        
        if name:
            lines.append(f"{domain}\t{flag}\t{path}\t{secure}\t{expires}\t{name}\t{value}")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def load_cookies(cookies_path: Path) -> Dict[str, str]:
    """
    Loads cookies from either JSON (Playwright storage_state) or Netscape format (.txt).
    Returns a name-value dictionary suitable for HTTP requests.
    """
    cookies_path = Path(cookies_path)
    if not cookies_path.exists():
        return {}
    
    cookies: Dict[str, str] = {}
    try:
        if cookies_path.suffix == ".json":
            with open(cookies_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for c in data.get("cookies", []):
                    cookies[c["name"]] = c["value"]
        elif cookies_path.suffix == ".txt":
            with open(cookies_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("#") or not line.strip():
                        continue
                    parts = line.strip().split("\t")
                    if len(parts) >= 7:
                        cookies[parts[5]] = parts[6]
    except Exception as e:
        print(f"[!] Warning reading cookies ({cookies_path}): {e}")
    return cookies
