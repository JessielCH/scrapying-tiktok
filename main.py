#!/usr/bin/env python3
"""
TikTok Scraper & Session Cookie Manager CLI
============================================
Unified command-line interface for session extraction, anti-detect scraping,
and watermark-free media downloads.

Examples:
  python main.py extract-cookies --mode guest
  python main.py extract-cookies --mode login
  python main.py scrape "https://www.tiktok.com/@user/video/1234567890" --download
"""

import sys
import argparse
from pathlib import Path

from src.cookie_manager import TikTokCookieManager
from src.scraper import TikTokScraper


def handle_extract_cookies(args):
    manager = TikTokCookieManager(output_dir=args.output)
    if args.mode == "guest":
        manager.extract_guest_cookies()
    elif args.mode == "login":
        manager.extract_login_cookies(timeout=args.timeout)


def handle_scrape(args):
    scraper = TikTokScraper(cookies_path=args.cookies, impersonate=args.impersonate)
    try:
        result = scraper.get_metadata(args.url)
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)

    if result["type"] == "video":
        data = result["data"]
        author = data.get("author", {})
        stats = data.get("stats", {})
        video = data.get("video", {})
        music = data.get("music", {})

        print("\n" + "=" * 55)
        print("📹 TIKTOK VIDEO DETAILS")
        print("=" * 55)
        print(f"ID:          {data.get('id')}")
        print(f"Author:      @{author.get('uniqueId')} ({author.get('nickname')})")
        print(f"Description: {data.get('desc')}")
        print(f"Metrics:     ❤️ {stats.get('diggCount', 0):,} likes | 💬 {stats.get('commentCount', 0):,} comments | 🔄 {stats.get('shareCount', 0):,} shares | 👁️ {stats.get('playCount', 0):,} views")
        print(f"Soundtrack:  {music.get('title')} - {music.get('authorName')}")
        
        play_addr = video.get("playAddr")
        print(f"CDN Stream:  {play_addr[:85]}..." if play_addr else "Unavailable")

        if args.download and play_addr:
            out_file = Path(args.out_dir) / f"{data.get('id', 'tiktok_video')}.mp4"
            scraper.download_video(play_addr, str(out_file))

    elif result["type"] == "user":
        data = result["data"]
        user = data.get("user", {})
        stats = data.get("stats", {})

        print("\n" + "=" * 55)
        print("👤 TIKTOK PROFILE DETAILS")
        print("=" * 55)
        print(f"Handle:      @{user.get('uniqueId')} ({user.get('nickname')})")
        print(f"Bio:         {user.get('signature')}")
        print(f"Verified:    {'Yes' if user.get('verified') else 'No'}")
        print(f"Followers:   {stats.get('followerCount', 0):,}")
        print(f"Following:   {stats.get('followingCount', 0):,}")
        print(f"Total Likes: {stats.get('heartCount', 0):,}")
        print(f"Videos:      {stats.get('videoCount', 0):,}")


def main():
    parser = argparse.ArgumentParser(
        description="TikTok Scraper & Session Cookie Manager CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: extract-cookies
    cookie_parser = subparsers.add_parser("extract-cookies", help="Extract TikTok session cookies")
    cookie_parser.add_argument(
        "--mode",
        choices=["guest", "login"],
        default="guest",
        help="Extraction mode: 'guest' (headless, fast) or 'login' (headed, QR/credentials)"
    )
    cookie_parser.add_argument(
        "--output",
        default="data",
        help="Output directory for cookies (default: data)"
    )
    cookie_parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout in seconds for interactive login (default: 300)"
    )

    # Subcommand: scrape
    scrape_parser = subparsers.add_parser("scrape", help="Scrape video or profile metadata and download media")
    scrape_parser.add_argument("url", help="TikTok video or profile URL")
    scrape_parser.add_argument(
        "--cookies",
        default="data/cookies.json",
        help="Path to session cookies file (.json or .txt)"
    )
    scrape_parser.add_argument(
        "--download",
        action="store_true",
        help="Download clean watermark-free video if target is a video URL"
    )
    scrape_parser.add_argument(
        "--out-dir",
        default="data/downloads",
        help="Output folder for downloaded media (default: data/downloads)"
    )
    scrape_parser.add_argument(
        "--impersonate",
        default="chrome120",
        help="Browser version to impersonate for TLS handshake (default: chrome120)"
    )

    args = parser.parse_args()

    if args.command == "extract-cookies":
        handle_extract_cookies(args)
    elif args.command == "scrape":
        handle_scrape(args)


if __name__ == "__main__":
    main()
