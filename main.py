#!/usr/bin/env python3
"""
CLI de Scraping y Gestor de Cookies de Sesión para TikTok
==========================================================
Interfaz de línea de comandos e interactiva para la extracción de sesiones,
scraping con anti-detección, análisis numérico de perfiles y métricas de publicaciones
(compatible con videos estándar y carruseles de fotos).

Uso:
  python main.py                              # Inicia la consola interactiva
  python main.py interactive                  # Inicia la consola interactiva
  python main.py analyze-user @usuario        # Análisis directo de usuario y posts
  python main.py extract-cookies --mode login # Extracción de cookies con login
  python main.py scrape <url> --download      # Scraping de publicación individual
"""

import sys
import json
import argparse
from pathlib import Path

# Configurar codificación UTF-8 para consola de Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from src.cookie_manager import TikTokCookieManager
from src.scraper import TikTokScraper
from src.user_analyzer import TikTokUserAnalyzer
from src.utils import export_posts_to_csv


def handle_extract_cookies(args):
    """Ejecuta la extracción de cookies."""
    manager = TikTokCookieManager(output_dir=args.output)
    if args.mode == "guest":
        manager.extract_guest_cookies()
    elif args.mode == "login":
        manager.extract_login_cookies(timeout=args.timeout)


def handle_analyze_user(args):
    """Ejecuta la extracción de perfil y el análisis numérico de videos y carruseles."""
    analyzer = TikTokUserAnalyzer(cookies_path=args.cookies, output_dir=args.output)
    try:
        report = analyzer.analyze_user(
            username=args.username,
            max_videos=args.max_videos,
            headed=args.headed,
            timeout=args.timeout
        )
    except Exception as e:
        print(f"[ERROR] Error al analizar el usuario: {e}")
        return

    profile = report["profile"]
    p_analysis = report["posts_analysis"]
    post_types = p_analysis["post_types"]
    totals = p_analysis["metrics_totals"]
    averages = p_analysis["metrics_averages"]
    perf = p_analysis["performance"]
    posts = p_analysis["posts"]

    print("\n" + "=" * 65)
    print("RESUMEN DEL PERFIL DE USUARIO EN TIKTOK")
    print("=" * 65)
    print(f"Usuario:                 {profile['username']}")
    print(f"Nombre Visible:          {profile['nickname']}")
    print(f"Biografía:               {profile['biography']}")
    print(f"Cuenta Verificada:       {'Sí' if profile['verified'] else 'No'}")
    print(f"Seguidos:                {profile['following_count']:,}")
    print(f"Seguidores:              {profile['follower_count']:,}")
    print(f"Total de Likes Recibidos:{profile['total_likes_received']:,}")
    print(f"Total de Videos:         {profile['total_videos_count']:,}")

    print("\n" + "=" * 65)
    print(f"ANALISIS NUMERICO: ULTIMOS {len(posts)} POSTS (VIDEOS Y CARRUSELES)")
    print("=" * 65)
    print(f"Publicaciones Analizadas: {len(posts)} ({post_types['videos_count']} videos, {post_types['carousels_count']} carruseles)")
    if post_types['carousels_count'] > 0:
        print(f"Total de Fotos en Carruseles: {post_types['total_carousel_images']}")
    print(f"Total de Likes:          {totals['likes']:,}")
    print(f"Total de Comentarios:    {totals['comments']:,}")
    print(f"Total Guardados (Favs):  {totals['saves']:,}")
    print(f"Total Compartidos:       {totals['shares']:,}")
    print(f"Total de Vistas:         {totals['views']:,}")
    print(f"Total de Interacciones:  {totals['total_interactions']:,}")
    print("-" * 65)
    print(f"Promedio de Likes:       {averages['avg_likes']:,}")
    print(f"Promedio de Comentarios: {averages['avg_comments']:,}")
    print(f"Promedio de Guardados:   {averages['avg_saves']:,}")
    print(f"Promedio de Compartidos: {averages['avg_shares']:,}")
    print(f"Promedio de Vistas:      {averages['avg_views']:,}")
    print(f"Tasa de Engagement:      {perf['engagement_rate_percent']}%")

    if posts:
        print("\n" + "=" * 65)
        print("DESGLOSE INDIVIDUAL DE PUBLICACIONES")
        print("=" * 65)
        for idx, p in enumerate(posts, 1):
            desc = (p['description'][:60] + "...") if len(p['description']) > 60 else p['description']
            type_badge = f"[CARRUSEL - {p['carousel_images_count']} diapositivas]" if p['is_carousel'] else "[VIDEO]"
            print(f"#{idx} {type_badge} [ID: {p['id']}]")
            print(f"   Descripción: {desc}")
            print(f"   Likes:       {p['likes']:,} | Comentarios: {p['comments']:,} | Guardados: {p['saves']:,}")
            print(f"   Compartidos: {p['shares']:,} | Vistas:      {p['views']:,}")
            print(f"   Enlace URL:  {p['url']}")

    clean_username = profile['username'].replace('@', '')

    # Exportar a JSON completo
    json_out = Path(args.json_out) if args.json_out else (Path(args.output) / f"analysis_{clean_username}.json")
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Exportar a CSV tabular (compatible con pandas DataFrame y Excel)
    csv_out = Path(args.output) / f"posts_{clean_username}.csv"
    export_posts_to_csv(posts, csv_out)

    print("\n" + "-" * 65)
    print(f"[OK] Datos tabulares exportados a CSV (DataFrame): {csv_out}")
    print(f"[OK] Reporte completo guardado en formato JSON:    {json_out}")
    print("-" * 65)


def handle_scrape(args):
    """Scrapea un video o publicación de carrusel de TikTok."""
    scraper = TikTokScraper(cookies_path=args.cookies, impersonate=args.impersonate)
    try:
        result = scraper.get_metadata(args.url)
    except Exception as e:
        print(f"[ERROR] {e}")
        return

    res_type = result.get("type")
    data = result.get("data", {})
    author = data.get("author", {})
    stats = data.get("stats", {})

    if res_type == "video":
        video = data.get("video", {})
        music = data.get("music", {})

        print("\n" + "=" * 55)
        print("DETALLES DEL VIDEO DE TIKTOK")
        print("=" * 55)
        print(f"ID:          {data.get('id')}")
        print(f"Autor:       @{author.get('uniqueId')} ({author.get('nickname')})")
        print(f"Descripción: {data.get('desc')}")
        print(f"Métricas:    Likes: {stats.get('diggCount', 0):,} | Comentarios: {stats.get('commentCount', 0):,} | Guardados: {stats.get('collectCount', 0):,} | Vistas: {stats.get('playCount', 0):,}")
        print(f"Música:      {music.get('title')} - {music.get('authorName')}")
        
        play_addr = video.get("playAddr")
        print(f"Enlace CDN:  {play_addr[:85]}..." if play_addr else "No disponible")

        if args.download and play_addr:
            out_file = Path(args.out_dir) / f"{data.get('id', 'tiktok_video')}.mp4"
            scraper.download_video(play_addr, str(out_file))

    elif res_type == "carousel":
        images = result.get("images", [])
        music = data.get("music", {})

        print("\n" + "=" * 55)
        print("DETALLES DEL CARRUSEL DE FOTOS")
        print("=" * 55)
        print(f"ID:          {data.get('id')}")
        print(f"Autor:       @{author.get('uniqueId')} ({author.get('nickname')})")
        print(f"Descripción: {data.get('desc')}")
        print(f"Diapositivas:{len(images)} fotos")
        print(f"Métricas:    Likes: {stats.get('diggCount', 0):,} | Comentarios: {stats.get('commentCount', 0):,} | Guardados: {stats.get('collectCount', 0):,} | Vistas: {stats.get('playCount', 0):,}")
        print(f"Música:      {music.get('title')} - {music.get('authorName')}")

        if args.download and images:
            carousel_dir = Path(args.out_dir) / f"carousel_{data.get('id', 'post')}"
            scraper.download_carousel_images(images, str(carousel_dir))

    elif res_type == "user":
        user = data.get("user", {})
        print("\n" + "=" * 55)
        print("DETALLES DEL PERFIL DE TIKTOK")
        print("=" * 55)
        print(f"Usuario:     @{user.get('uniqueId')} ({user.get('nickname')})")
        print(f"Biografía:   {user.get('signature')}")
        print(f"Verificado:  {'Sí' if user.get('verified') else 'No'}")
        print(f"Seguidores:  {stats.get('followerCount', 0):,}")
        print(f"Seguidos:    {stats.get('followingCount', 0):,}")
        print(f"Total Likes: {stats.get('heartCount', 0):,}")
        print(f"Videos:      {stats.get('videoCount', 0):,}")


def run_interactive_menu():
    """Menú interactivo por consola en texto."""
    while True:
        print("\n" + "=" * 68)
        print("          TIKTOK SCRAPER & ANALIZADOR DE RENDIMIENTO              ")
        print("=" * 68)
        print(" [1] Analizar Perfil y Publicaciones (Exportar a CSV / DataFrame)")
        print(" [2] Extraer Cookies de Sesion (Modo Invitado o Login con QR)")
        print(" [3] Consultar Publicacion Individual (Inspeccionar Metadatos)")
        print(" [4] Salir")
        print("=" * 68)

        choice = input("\nSelecciona una opción [1-4]: ").strip()

        if choice == "1":
            username = input("\nIngresa el usuario de TikTok (ej. @mrbeast o enlace del perfil): ").strip()
            if not username:
                print("[!] El nombre de usuario no puede estar vacío.")
                continue

            count_input = input("Número de publicaciones recientes a analizar [por defecto 10]: ").strip()
            max_videos = int(count_input) if count_input.isdigit() else 10

            headed_input = input("¿Abrir navegador visible para resolver el rompecabezas de captcha si aparece? (s/N) [por defecto N]: ").strip().lower()
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
            input("\nPresiona Enter para regresar al menú principal...")

        elif choice == "2":
            print("\nSelecciona el modo de extracción de cookies:")
            print("  [1] Modo Invitado (Automático, sin ventana, cookies públicas como ttwid)")
            print("  [2] Modo Login (Abre navegador Chromium para escanear QR / iniciar sesión)")
            mode_choice = input("Opción [1/2, por defecto 1]: ").strip()
            mode = "login" if mode_choice == "2" else "guest"

            class Args:
                pass
            args = Args()
            args.mode = mode
            args.output = "data"
            args.timeout = 300

            handle_extract_cookies(args)
            input("\nPresiona Enter para regresar al menú principal...")

        elif choice == "3":
            url = input("\nIngresa la URL del video o carrusel de TikTok: ").strip()
            if not url:
                print("[!] La URL no puede estar vacía.")
                continue

            dl_input = input("¿Deseas descargar el archivo multimedia (video MP4 o fotos del carrusel)? (s/N) [por defecto N]: ").strip().lower()
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
            input("\nPresiona Enter para regresar al menú principal...")

        elif choice in ["4", "exit", "quit", "q", "salir"]:
            print("\nSesión finalizada.\n")
            sys.exit(0)

        else:
            print("[!] Opción inválida. Por favor ingresa 1, 2, 3 o 4.")


def main():
    # Si no se pasan argumentos o se especifica "interactive", iniciar el menú interactivo
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1].lower() in ["interactive", "-i", "--interactive", "interactivo"]):
        run_interactive_menu()
        return

    parser = argparse.ArgumentParser(
        description="CLI de Scraping y Gestor de Cookies de Sesión para TikTok",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcomando: interactive
    subparsers.add_parser("interactive", help="Iniciar menú interactivo en consola")

    # Subcomando: extract-cookies
    cookie_parser = subparsers.add_parser("extract-cookies", help="Extraer cookies de sesión de TikTok")
    cookie_parser.add_argument(
        "--mode",
        choices=["guest", "login"],
        default="guest",
        help="Modo de extracción: 'guest' (automático, sin ventana) o 'login' (con ventana, escaneo QR)"
    )
    cookie_parser.add_argument(
        "--output",
        default="data",
        help="Directorio de salida para las cookies (por defecto: data)"
    )
    cookie_parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Tiempo límite en segundos para el inicio de sesión interactivo (por defecto: 300)"
    )

    # Subcomando: scrape
    scrape_parser = subparsers.add_parser("scrape", help="Scrapear metadatos de video o carrusel y descargar multimedia")
    scrape_parser.add_argument("url", help="URL del video, carrusel o perfil de TikTok")
    scrape_parser.add_argument(
        "--cookies",
        default="data/cookies.json",
        help="Ruta al archivo de cookies (.json o .txt)"
    )
    scrape_parser.add_argument(
        "--download",
        action="store_true",
        help="Descargar video sin marca de agua o fotos del carrusel"
    )
    scrape_parser.add_argument(
        "--out-dir",
        default="data/downloads",
        help="Carpeta de destino para los archivos descargados (por defecto: data/downloads)"
    )
    scrape_parser.add_argument(
        "--impersonate",
        default="chrome120",
        help="Versión de navegador para la firma TLS (por defecto: chrome120)"
    )

    # Subcomando: analyze-user
    user_parser = subparsers.add_parser("analyze-user", help="Extraer biografía/métricas de perfil y analizar numéricamente los últimos posts")
    user_parser.add_argument("username", help="Nombre de usuario de TikTok (ej. @mrbeast o mrbeast)")
    user_parser.add_argument(
        "--max-videos",
        type=int,
        default=10,
        help="Número máximo de publicaciones recientes a analizar (por defecto: 10)"
    )
    user_parser.add_argument(
        "--cookies",
        default="data/cookies.json",
        help="Ruta al archivo de cookies de sesión (.json o .txt)"
    )
    user_parser.add_argument(
        "--output",
        default="data",
        help="Carpeta de destino para los reportes generados (por defecto: data)"
    )
    user_parser.add_argument(
        "--json-out",
        default=None,
        help="Nombre de archivo JSON personalizado para guardar el análisis"
    )
    user_parser.add_argument(
        "--headed",
        action="store_true",
        help="Abrir navegador en modo visible para resolver captcha de rompecabezas si es necesario"
    )
    user_parser.add_argument(
        "--timeout",
        type=int,
        default=35,
        help="Tiempo límite de carga de página en segundos (por defecto: 35)"
    )

    args = parser.parse_args()

    if args.command in ["interactive", "interactivo"]:
        run_interactive_menu()
    elif args.command == "extract-cookies":
        handle_extract_cookies(args)
    elif args.command == "scrape":
        handle_scrape(args)
    elif args.command == "analyze-user":
        handle_analyze_user(args)


if __name__ == "__main__":
    main()
