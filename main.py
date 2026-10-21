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
    manager = TikTokCookieManager(output_dir=args.output)
    if args.mode == "guest":
        manager.extract_guest_cookies()
    elif args.mode == "login":
        manager.extract_login_cookies(timeout=args.timeout)


def handle_analyze_user(args):
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
        sys.exit(1)

    profile = report["profile"]
    v_analysis = report["videos_analysis"]
    totals = v_analysis["metrics_totals"]
    averages = v_analysis["metrics_averages"]
    perf = v_analysis["performance"]
    videos = v_analysis["videos"]

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
    print(f"📊 NUMERICAL ANALYSIS: LAST {len(videos)} VIDEOS")
    print("=" * 65)
    print(f"Total Likes:            {totals['likes']:,}")
    print(f"Total Comments:         {totals['comments']:,}")
    print(f"Total Saves (Bookmarks):{totals['saves']:,}")
    print(f"Total Shares:           {totals['shares']:,}")
    print(f"Total Views:            {totals['views']:,}")
    print(f"Total Interactions:     {totals['total_interactions']:,}")
    print("-" * 65)
    print(f"Average Likes/Video:    {averages['avg_likes']:,}")
    print(f"Average Comments/Video: {averages['avg_comments']:,}")
    print(f"Average Saves/Video:    {averages['avg_saves']:,}")
    print(f"Average Shares/Video:   {averages['avg_shares']:,}")
    print(f"Average Views/Video:    {averages['avg_views']:,}")
    print(f"Engagement Rate (Views):{perf['engagement_rate_percent']}%")

    if videos:
        print("\n" + "=" * 65)
        print("🎬 INDIVIDUAL VIDEO BREAKDOWN")
        print("=" * 65)
        for idx, vid in enumerate(videos, 1):
            desc = (vid['description'][:60] + "...") if len(vid['description']) > 60 else vid['description']
            print(f"#{idx} [ID: {vid['video_id']}]")
            print(f"   Caption:  {desc}")
            print(f"   Likes:    {vid['likes']:,} | Comments: {vid['comments']:,} | Saves: {vid['saves']:,}")
            print(f"   Shares:   {vid['shares']:,} | Views:    {vid['views']:,}")
            print(f"   URL:      {vid['url']}")

    # Export to JSON
    json_out = Path(args.json_out) if args.json_out else (Path(args.output) / f"analysis_{profile['username'].replace('@', '')}.json")
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n[✓] Detailed JSON analysis saved to: {json_out}")


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

    # Subcommand: analyze-user
    user_parser = subparsers.add_parser("analyze-user", help="Extract profile bio/stats and analyze last 10 videos numerically")
    user_parser.add_argument("username", help="TikTok username (e.g. @mrbeast or mrbeast)")
    user_parser.add_argument(
        "--max-videos",
        type=int,
        default=10,
        help="Maximum number of recent videos to analyze (default: 10)"
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

    if args.command == "extract-cookies":
        handle_extract_cookies(args)
    elif args.command == "scrape":
        handle_scrape(args)
    elif args.command == "analyze-user":
        handle_analyze_user(args)


if __name__ == "__main__":
    main()
