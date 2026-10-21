#!/usr/bin/env python3
"""
TikTok Scraper & Session Cookie Manager CLI
============================================
Unified interactive and command-line interface for session extraction,
anti-detect scraping, profile metrics analysis, and watermark-free media downloads
(supporting both standard videos and photo carousels).

Usage:
  python main.py                              # Launches Interactive Console
  python main.py interactive                  # Launches Interactive Console
  python main.py analyze-user @username       # Direct CLI user & post analysis
  python main.py extract-cookies --mode login # Direct CLI cookie extraction
  python main.py scrape <url> --download      # Direct CLI single post scraper
"""

import sys
import json
import argparse
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from src.cookie_manager import TikTokCookieManager
from src.scraper import TikTokScraper
from src.user_analyzer import TikTokUserAnalyzer


def handle_extract_cookies(args):
    """Executes cookie extraction."""
    manager = TikTokCookieManager(output_dir=args.output)
    if args.mode == "guest":
        manager.extract_guest_cookies()
    elif args.mode == "login":
        manager.extract_login_cookies(timeout=args.timeout)


def handle_analyze_user(args):
    """Executes user profile extraction and numerical engagement analysis on videos and carousels."""
    analyzer = TikTokUserAnalyzer(cookies_path=args.cookies, output_dir=args.output)
    try:
        report = analyzer.analyze_user(
            username=args.username,
            max_videos=args.max_videos,
            headed=args.headed,
            timeout=args.timeout
        )
    except Exception as e:
        print(f"[!] Error analyzing user: {e}")
        return

    profile = report["profile"]
    p_analysis = report["posts_analysis"]
    post_types = p_analysis["post_types"]
    totals = p_analysis["metrics_totals"]
    averages = p_analysis["metrics_averages"]
    perf = p_analysis["performance"]
    posts = p_analysis["posts"]

    print("\n" + "=" * 65)
    print("👤 TIKTOK USER PROFILE OVERVIEW")
    print("=" * 65)
    print(f"Username:        {profile['username']}")
    print(f"Display Name:    {profile['nickname']}")
    print(f"Biography:       {profile['biography']}")
    print(f"Verified:        {'Yes' if profile['verified'] else 'No'}")
    print(f"Following:       {profile['following_count']:,}")
    print(f"Followers:       {profile['follower_count']:,}")
    print(f"Total Likes:     {profile['total_likes_received']:,}")
    print(f"Total Videos:    {profile['total_videos_count']:,}")

    print("\n" + "=" * 65)
    print(f"📊 NUMERICAL ANALYSIS: LAST {len(posts)} POSTS (VIDEOS & CAROUSELS)")
    print("=" * 65)
    print(f"Posts Analyzed:         {len(posts)} ({post_types['videos_count']} videos, {post_types['carousels_count']} carousels)")
    if post_types['carousels_count'] > 0:
        print(f"Total Carousel Slides:  {post_types['total_carousel_images']}")
    print(f"Total Likes:            {totals['likes']:,}")
    print(f"Total Comments:         {totals['comments']:,}")
    print(f"Total Saves (Bookmarks):{totals['saves']:,}")
    print(f"Total Shares:           {totals['shares']:,}")
    print(f"Total Views:            {totals['views']:,}")
    print(f"Total Interactions:     {totals['total_interactions']:,}")
    print("-" * 65)
    print(f"Average Likes/Post:     {averages['avg_likes']:,}")
    print(f"Average Comments/Post:  {averages['avg_comments']:,}")
    print(f"Average Saves/Post:     {averages['avg_saves']:,}")
    print(f"Average Shares/Post:    {averages['avg_shares']:,}")
    print(f"Average Views/Post:     {averages['avg_views']:,}")
    print(f"Engagement Rate (Views):{perf['engagement_rate_percent']}%")

    if posts:
        print("\n" + "=" * 65)
        print("🎬 INDIVIDUAL POST BREAKDOWN")
        print("=" * 65)
        for idx, p in enumerate(posts, 1):
            desc = (p['description'][:60] + "...") if len(p['description']) > 60 else p['description']
            type_badge = f"[CAROUSEL 📸 - {p['carousel_images_count']} slides]" if p['is_carousel'] else "[VIDEO 🎬]"
            print(f"#{idx} {type_badge} [ID: {p['id']}]")
            print(f"   Caption:  {desc}")
            print(f"   Likes:    {p['likes']:,} | Comments: {p['comments']:,} | Saves: {p['saves']:,}")
            print(f"   Shares:   {p['shares']:,} | Views:    {p['views']:,}")
            print(f"   URL:      {p['url']}")

    # Export to JSON
    json_out = Path(args.json_out) if args.json_out else (Path(args.output) / f"analysis_{profile['username'].replace('@', '')}.json")
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n[✓] Detailed JSON analysis saved to: {json_out}")


def handle_scrape(args):
    """Scrapes a single TikTok video or carousel post."""
    scraper = TikTokScraper(cookies_path=args.cookies, impersonate=args.impersonate)
    try:
        result = scraper.get_metadata(args.url)
    except Exception as e:
        print(f"[!] Error: {e}")
        return

    res_type = result.get("type")
    data = result.get("data", {})
    author = data.get("author", {})
    stats = data.get("stats", {})

    if res_type == "video":
        video = data.get("video", {})
        music = data.get("music", {})

        print("\n" + "=" * 55)
        print("📹 TIKTOK VIDEO DETAILS")
        print("=" * 55)
        print(f"ID:          {data.get('id')}")
        print(f"Author:      @{author.get('uniqueId')} ({author.get('nickname')})")
        print(f"Description: {data.get('desc')}")
        print(f"Metrics:     ❤️ {stats.get('diggCount', 0):,} likes | 💬 {stats.get('commentCount', 0):,} comments | 🔖 {stats.get('collectCount', 0):,} saves | 👁️ {stats.get('playCount', 0):,} views")
        print(f"Soundtrack:  {music.get('title')} - {music.get('authorName')}")
        
        play_addr = video.get("playAddr")
        print(f"CDN Stream:  {play_addr[:85]}..." if play_addr else "Unavailable")

        if args.download and play_addr:
            out_file = Path(args.out_dir) / f"{data.get('id', 'tiktok_video')}.mp4"
            scraper.download_video(play_addr, str(out_file))

    elif res_type == "carousel":
        images = result.get("images", [])
        music = data.get("music", {})

        print("\n" + "=" * 55)
        print("📸 TIKTOK PHOTO CAROUSEL DETAILS")
        print("=" * 55)
        print(f"ID:          {data.get('id')}")
        print(f"Author:      @{author.get('uniqueId')} ({author.get('nickname')})")
        print(f"Description: {data.get('desc')}")
        print(f"Slides:      {len(images)} photos")
        print(f"Metrics:     ❤️ {stats.get('diggCount', 0):,} likes | 💬 {stats.get('commentCount', 0):,} comments | 🔖 {stats.get('collectCount', 0):,} saves | 👁️ {stats.get('playCount', 0):,} views")
        print(f"Soundtrack:  {music.get('title')} - {music.get('authorName')}")

        if args.download and images:
            carousel_dir = Path(args.out_dir) / f"carousel_{data.get('id', 'post')}"
            scraper.download_carousel_images(images, str(carousel_dir))

    elif res_type == "user":
        user = data.get("user", {})
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


def run_interactive_menu():
    """Interactive text-based console menu."""
    while True:
        print("\n" + "=" * 68)
        print("     🔥 TIKTOK SCRAPER & ENGAGEMENT ANALYZER (INTERACTIVE) 🔥     ")
        print("=" * 68)
        print(" [1] 👤 Analyze User Profile & Latest Posts (Videos + Carousels)")
        print(" [2] 🍪 Extract Session Cookies (Guest Mode or Login QR)")
        print(" [3] 📥 Scrape Single Post / Download Media (Video or Carousel)")
        print(" [4] ❌ Exit")
        print("=" * 68)

        choice = input("\nSelect an option [1-4]: ").strip()

        if choice == "1":
            username = input("\nEnter TikTok username (e.g. @mrbeast or full URL): ").strip()
            if not username:
                print("[!] Username cannot be empty.")
                continue

            count_input = input("Number of recent posts to analyze [default 10]: ").strip()
            max_videos = int(count_input) if count_input.isdigit() else 10

            headed_input = input("Run visible browser to solve captcha puzzle if needed? (y/N) [default N]: ").strip().lower()
            headed = headed_input in ["y", "yes", "s", "si"]

            class Args:
                pass
            args = Args()
            args.username = username
            args.max_videos = max_videos
            args.headed = headed
            args.cookies = "data/cookies.json"
            args.output = "data"
            args.json_out = None
            args.timeout = 40

            handle_analyze_user(args)
            input("\nPress Enter to return to main menu...")

        elif choice == "2":
            print("\nSelect cookie extraction mode:")
            print("  [1] Guest Mode (Headless, fast public cookies like ttwid)")
            print("  [2] Login Mode (Visible Chromium browser for QR scan / login)")
            mode_choice = input("Option [1/2, default 1]: ").strip()
            mode = "login" if mode_choice == "2" else "guest"

            class Args:
                pass
            args = Args()
            args.mode = mode
            args.output = "data"
            args.timeout = 300

            handle_extract_cookies(args)
            input("\nPress Enter to return to main menu...")

        elif choice == "3":
            url = input("\nEnter TikTok video or carousel URL: ").strip()
            if not url:
                print("[!] URL cannot be empty.")
                continue

            dl_input = input("Download media (video file or carousel slides)? (y/N) [default N]: ").strip().lower()
            download = dl_input in ["y", "yes", "s", "si"]

            class Args:
                pass
            args = Args()
            args.url = url
            args.cookies = "data/cookies.json"
            args.download = download
            args.out_dir = "data/downloads"
            args.impersonate = "chrome120"

            handle_scrape(args)
            input("\nPress Enter to return to main menu...")

        elif choice in ["4", "exit", "quit", "q"]:
            print("\nGoodbye!\n")
            sys.exit(0)

        else:
            print("[!] Invalid option. Please enter 1, 2, 3, or 4.")


def main():
    # If no arguments are passed or "interactive" is specified, launch interactive console
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1].lower() in ["interactive", "-i", "--interactive"]):
        run_interactive_menu()
        return

    parser = argparse.ArgumentParser(
        description="TikTok Scraper & Session Cookie Manager CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: interactive
    subparsers.add_parser("interactive", help="Start interactive console menu")

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
        help="Download clean watermark-free video or carousel images"
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

    # Subcommand: analyze-user
    user_parser = subparsers.add_parser("analyze-user", help="Extract profile bio/stats and analyze last 10 posts numerically")
    user_parser.add_argument("username", help="TikTok username (e.g. @mrbeast or mrbeast)")
    user_parser.add_argument(
        "--max-videos",
        type=int,
        default=10,
        help="Maximum number of recent posts to analyze (default: 10)"
    )
    user_parser.add_argument(
        "--cookies",
        default="data/cookies.json",
        help="Path to session cookies file (.json or .txt)"
    )
    user_parser.add_argument(
        "--output",
        default="data",
        help="Output folder for generated reports (default: data)"
    )
    user_parser.add_argument(
        "--json-out",
        default=None,
        help="Custom JSON filename for exported analysis"
    )
    user_parser.add_argument(
        "--headed",
        action="store_true",
        help="Run browser in visible mode to solve captcha puzzle if requested"
    )
    user_parser.add_argument(
        "--timeout",
        type=int,
        default=35,
        help="Page load timeout in seconds (default: 35)"
    )

    args = parser.parse_args()

    if args.command == "interactive":
        run_interactive_menu()
    elif args.command == "extract-cookies":
        handle_extract_cookies(args)
    elif args.command == "scrape":
        handle_scrape(args)
    elif args.command == "analyze-user":
        handle_analyze_user(args)


if __name__ == "__main__":
    main()
