#!/usr/bin/env python3
"""
CLI de Auditoría Demográfica, Psicometría y Servidor API
=========================================================
Punto de entrada unificado para el backend de Anti-Gravity ID / Monorepo:
- Servidor FastAPI para conexión en tiempo real con el Frontend.
- Menú interactivo por consola con soporte para auditoría completa y forense.
- Subcomandos de terminal para automatización e integración continua.
"""

import sys
import json
import argparse
from pathlib import Path

# Configurar codificación UTF-8 para consola de Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Asegurar que el directorio backend esté en el sys.path
backend_root = Path(__file__).resolve().parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

# Importación ligera para arranque instantáneo del menú
from src.cookie_manager import TikTokCookieManager



def safe_input(prompt: str, default: str = "") -> str:
    """Función de entrada segura que evita excepciones EOFError o KeyboardInterrupt."""
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        return default


def start_api_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = True):
    """Inicia el servidor REST de FastAPI con uvicorn."""
    try:
        import uvicorn
    except ImportError:
        print("[!] uvicorn no está instalado. Instálalo con: pip install uvicorn fastapi")
        return

    print("\n" + "=" * 68)
    print(f"[*] Iniciando servidor API de Extracción en http://{host}:{port}")
    print(f"[*] Documentación interactiva Swagger: http://{host}:{port}/docs")
    print("=" * 68 + "\n")
    uvicorn.run("api.app:app", host=host, port=port, reload=reload)


def run_full_audit(url: str, sample_comments: int = 150, download_evidence: bool = True, headed: bool = False):
    """Ejecuta el pipeline completo de extracción y psicometría."""
    from src.forensic_vault import ForensicVault
    from src.comment_scraper import TikTokCommentScraper
    from src.privacy_dp import AudienceQualityAnalyzer
    from src.nlp_engine import PsychometricsNLPEngine
    from src.gemini_synthesizer import GeminiRiskSynthesizer

    print("\n" + "=" * 68)
    print(f"[*] INICIANDO EXTRACCIÓN Y ANÁLISIS DE CONTENIDOS Y PSICOMETRÍA")
    print(f"[*] Objetivo: {url}")
    print("=" * 68)

    # 1. Preservación Multimedia
    vault = ForensicVault(evidence_dir="data/evidence", cookies_txt_path="data/cookies.txt")
    evidence_manifest = None
    if download_evidence and ("/video/" in url or "/photo/" in url):
        try:
            import re
            vid_match = re.search(r"/(?:video|photo)/(\d+)", url)
            vid = vid_match.group(1) if vid_match else "unknown"
            evidence_manifest = vault.capture_evidence(video_url=url, video_id=vid)
        except Exception as e:
            print(f"[!] Aviso al preservar copia del video: {e}")

    # 2. Extracción y Anonimización SHA-256 de Comentarios
    comment_scraper = TikTokCommentScraper(cookies_path="data/cookies.json", output_dir="data")
    comments = comment_scraper.scrape_comments(post_url=url, max_comments=sample_comments, headed=headed)

    # 3. Métricas AQS
    aqs_data = AudienceQualityAnalyzer.calculate_aqs_and_markers(comments, engagement_rate=5.0)

    # 4. Pipeline NLP (Zero-Shot + ε-DP)
    nlp = PsychometricsNLPEngine()
    nlp_results = nlp.analyze_comment_batch(comments)

    # 5. Síntesis Gemini 3.8 Flash
    synthesizer = GeminiRiskSynthesizer()
    payload = {
        "url": url,
        "sample_size": len(comments),
        "age_distribution_percent": nlp_results["age_distribution_percent"],
        "big_five_scores": nlp_results["big_five_scores"],
        "aqs_score": aqs_data["aqs_score"],
        "dominant_emotion": nlp_results["dominant_emotion"],
        "evidence_sha256": (evidence_manifest or {}).get("sha256_hash", "NO_EVID")
    }
    ai_verdict = synthesizer.synthesize(payload)

    print("\n" + "=" * 68)
    print("RESULTADOS DE LA EXTRACCIÓN PSICOMÉTRICA Y BRAND SAFETY")
    print("=" * 68)
    print(f"Muestra de Comentarios:   {len(comments)} (Anonimizados con SHA-256)")
    print(f"Puntaje AQS (Calidad):    {aqs_data['aqs_score']} / 100")
    print(f"Nivel de Riesgo (Score):  {ai_verdict.get('risk_score', 0)} / 100 [{ai_verdict.get('risk_level', 'N/A')}]")
    print(f"Apto para Brand Safety:   {'SÍ' if ai_verdict.get('brand_safety_eligible') else 'NO (Riesgo detectado)'}")
    print(f"Alerta Control Parental:  {'ACTIVADA (Supervisión requerida)' if ai_verdict.get('parental_alert_triggered') else 'DESACTIVADA'}")
    print("-" * 68)
    print("DISTRIBUCIÓN DE EDAD REAL (PRIVACIDAD DIFERENCIAL ε-DP):")
    for age_group, pct in nlp_results["age_distribution_percent"].items():
        print(f"  • {age_group}: {pct}%")
    print("-" * 68)
    print("PERFIL PSICOMÉTRICO (BIG FIVE):")
    for trait, val in nlp_results["big_five_scores"].items():
        print(f"  • {trait.replace('_', ' ').capitalize()}: {val}")
    print("\n" + "=" * 68)
    print("DICTAMEN EJECUTIVO (GEMINI 3.8 FLASH):")
    print("=" * 68)
    print(ai_verdict.get("conclusion_narrativa_global", ""))
    print("=" * 68 + "\n")


def run_interactive_menu():
    """Menú interactivo por terminal."""
    cookie_mgr = TikTokCookieManager(output_dir="data")

    while True:
        if cookie_mgr.is_authenticated():
            session_status = "[AUTENTICADA - Sesión completa]"
        elif cookie_mgr.has_valid_cookies():
            session_status = "[INVITADO - Cookies públicas]"
        else:
            session_status = "[NO DETECTADA - OBLIGATORIO EXTRAER]"

        print("\n" + "=" * 68)
        print("     SISTEMA DE EXTRACCIÓN Y ANÁLISIS DEMOGRÁFICO (BACKEND)       ")
        print("=" * 68)
        print(f" Estado de Sesión: {session_status}")
        print("-" * 68)
        print(" [1] Analizar Perfil y Publicaciones (Exportar CSVs y JSON)")
        print(" [2] Extraer / Renovar Cookies de Sesión (Login QR o Invitado)")
        print(" [3] Extracción Integral (Métricas + NLP Big Five + Gemini)")
        print(" [4] Iniciar Servidor API REST (para conectar con el Frontend)")
        print(" [5] Salir")
        print("=" * 68)

        choice = safe_input("\nSelecciona una opción [1-5]: ", default="5")

        if choice == "1":
            if not cookie_mgr.has_valid_cookies():
                cookie_mgr.ensure_cookies()
            username = safe_input("\nIngresa el usuario de TikTok (ej. @mrbeast): ")
            if username:
                from src.user_analyzer import TikTokUserAnalyzer
                analyzer = TikTokUserAnalyzer(cookies_path="data/cookies.json", output_dir="data")
                analyzer.analyze_user(username=username, max_videos=10, headed=True)
            safe_input("\nPresiona Enter para volver...")

        elif choice == "2":
            mode_choice = safe_input("Modo: [1] Invitado / [2] Login QR [por defecto 1]: ", default="1")
            if mode_choice == "2":
                cookie_mgr.extract_login_cookies(timeout=300)
            else:
                cookie_mgr.extract_guest_cookies()
            safe_input("\nPresiona Enter para volver...")

        elif choice == "3":
            url = safe_input("\nIngresa la URL del video o perfil de TikTok a analizar: ")
            if url:
                run_full_audit(url, sample_comments=150, download_evidence=True, headed=False)
            safe_input("\nPresiona Enter para volver...")

        elif choice == "4":
            start_api_server(host="127.0.0.1", port=8000)

        elif choice in ["5", "exit", "quit", "q", "salir"]:
            print("\nSesión finalizada.\n")
            sys.exit(0)


def main():
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1].lower() in ["interactive", "-i"]):
        run_interactive_menu()
        return

    parser = argparse.ArgumentParser(description="Backend de Auditoría Demográfica y Psicometría")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcomando: server
    server_parser = subparsers.add_parser("server", help="Iniciar servidor API REST de FastAPI")
    server_parser.add_argument("--host", default="127.0.0.1", help="Host del servidor")
    server_parser.add_argument("--port", type=int, default=8000, help="Puerto del servidor")

    # Subcomando: audit
    audit_parser = subparsers.add_parser("audit", help="Ejecutar auditoría forense y psicométrica completa")
    audit_parser.add_argument("url", help="URL del video o perfil de TikTok")
    audit_parser.add_argument("--sample", type=int, default=150, help="Número de comentarios a extraer")
    audit_parser.add_argument("--no-evidence", action="store_true", help="Omitir descarga de video")

    args = parser.parse_args()

    if args.command == "server":
        start_api_server(host=args.host, port=args.port)
    elif args.command == "audit":
        run_full_audit(url=args.url, sample_comments=args.sample, download_evidence=not args.no_evidence)


if __name__ == "__main__":
    main()
