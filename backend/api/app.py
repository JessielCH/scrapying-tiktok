"""
Servidor FastAPI para Auditoría Demográfica, Psicometría y Evidencia Forense
=============================================================================
Expone los servicios de extracción, cálculo de privacidad diferencial,
clasificación Zero-Shot Big Five y síntesis ejecutiva con Gemini 1.5 Flash.
"""

import os
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .schemas import AuditRequest, AuditResponse, TargetMetadata, DemographicsReport, RiskAssessmentReport

import sys
from pathlib import Path

# Asegurar que el directorio raíz de backend esté en sys.path
backend_root = Path(__file__).resolve().parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

try:
    from src.cookie_manager import TikTokCookieManager
    from src.comment_scraper import TikTokCommentScraper
    from src.forensic_vault import ForensicVault
    from src.privacy_dp import AudienceQualityAnalyzer
    from src.nlp_engine import PsychometricsNLPEngine
    from src.gemini_synthesizer import GeminiRiskSynthesizer
except ImportError:
    from ..src.cookie_manager import TikTokCookieManager
    from ..src.comment_scraper import TikTokCommentScraper
    from ..src.forensic_vault import ForensicVault
    from ..src.privacy_dp import AudienceQualityAnalyzer
    from ..src.nlp_engine import PsychometricsNLPEngine
    from ..src.gemini_synthesizer import GeminiRiskSynthesizer

app = FastAPI(
    title="Auditoría Demográfica y Psicometría en Redes Sociales API",
    description="Motor de análisis lingüístico, estimación etaria, evidencia forense inmutable y brand safety.",
    version="1.0.0"
)

# Configuración de CORS para conectar sin restricciones con el Frontend (Vite/React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialización de dependencias y servicios
DATA_DIR = Path(os.getenv("DATA_DIR", Path(__file__).resolve().parent.parent / "data"))
EVIDENCE_DIR = DATA_DIR / "evidence"
REPORTS_DIR = DATA_DIR / "reports"

cookie_manager = TikTokCookieManager(output_dir=str(DATA_DIR))
forensic_vault = ForensicVault(evidence_dir=str(EVIDENCE_DIR), cookies_txt_path=str(DATA_DIR / "cookies.txt"))
nlp_engine = PsychometricsNLPEngine(epsilon=float(os.getenv("DP_EPSILON", 1.0)))
gemini_synthesizer = GeminiRiskSynthesizer()


def extract_video_id(url: str) -> str:
    """Extrae el ID numérico del video de una URL de TikTok."""
    match = re.search(r"/(?:video|photo)/(\d+)", url)
    if match:
        return match.group(1)
    # Si es perfil u otra estructura, generar un identificador basado en hash
    cleaned = re.sub(r"[^a-zA-Z0-9]", "_", url.strip())[:32]
    return f"target_{cleaned}"


def extract_creator_handle(url: str) -> str:
    """Extrae el handle de usuario de la URL."""
    match = re.search(r"@([a-zA-Z0-9_.-]+)", url)
    return f"@{match.group(1)}" if match else "@creador_tiktok"


@app.get("/api/v1/health")
def health_check():
    """Verifica el estado del servicio y la vigencia de las cookies de sesión."""
    has_cookies = cookie_manager.has_valid_cookies()
    is_auth = cookie_manager.is_authenticated()
    return {
        "status": "OPERATIONAL",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "cookies_valid": has_cookies,
        "is_authenticated": is_auth,
        "mode": "AUTHENTICATED" if is_auth else ("GUEST" if has_cookies else "UNCONFIGURED"),
        "gemini_configured": gemini_synthesizer.client is not None
    }


@app.post("/api/v1/audit", response_model=AuditResponse)
async def perform_audit(request: AuditRequest):
    """
    Ejecuta el ciclo de auditoría completo:
    1. Preservación forense del video (yt-dlp + hash SHA-256).
    2. Extracción de comentarios con anonimización en memoria SHA-256 (LOPDP).
    3. Análisis AQS y marcadores psicolingüísticos.
    4. Inferencia Zero-Shot Big Five y edad con Privacidad Diferencial (ε-DP).
    5. Síntesis ejecutiva y evaluación de riesgo con Gemini 1.5 Flash.
    """
    url = request.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="Debe proporcionar una URL válida de TikTok.")

    video_id = extract_video_id(url)
    creator = extract_creator_handle(url)
    timestamp_utc = datetime.now(timezone.utc).isoformat()

    # 1. Bóveda Forense Inmutable
    evidence_url = None
    evidence_sha256 = None
    if request.download_evidence and ("/video/" in url or "/photo/" in url):
        try:
            manifest = forensic_vault.capture_evidence(
                video_url=url,
                video_id=video_id,
                creator=creator
            )
            evidence_url = f"/api/v1/evidence/{manifest['local_file_name']}"
            evidence_sha256 = manifest["sha256_hash"]
        except Exception as e:
            print(f"[!] Aviso al preservar evidencia forense: {e}")
            evidence_sha256 = "EVID_PENDING_OR_PROFILE"

    # 2. Extracción de Comentarios con Anonimización SHA-256
    scraper = TikTokCommentScraper(
        cookies_path=str(DATA_DIR / "cookies.json"),
        output_dir=str(DATA_DIR)
    )
    comments = await scraper.scrape_comments_async(
        post_url=url,
        max_comments=request.sample_comments,
        headed=request.headed_browser
    )

    # 3. Calidad de Audiencia (AQS)
    aqs_data = AudienceQualityAnalyzer.calculate_aqs_and_markers(comments, engagement_rate=5.5)

    # 4. Pipeline NLP (mDeBERTa-v3 + Privacidad Diferencial Laplace)
    nlp_results = nlp_engine.analyze_comment_batch(comments)

    # 5. Síntesis Ejecutiva con Gemini 1.5 Flash
    synthesis_payload = {
        "creator": creator,
        "video_id": video_id,
        "sample_size": len(comments),
        "age_distribution_percent": nlp_results["age_distribution_percent"],
        "big_five_scores": nlp_results["big_five_scores"],
        "aqs_score": aqs_data["aqs_score"],
        "dominant_emotion": nlp_results["dominant_emotion"],
        "evidence_sha256": evidence_sha256
    }
    ai_verdict = gemini_synthesizer.synthesize(synthesis_payload)

    # Armado del Contrato de Respuesta
    response_payload = AuditResponse(
        success=True,
        target=TargetMetadata(
            url=url,
            creator=creator,
            video_id=video_id,
            categories=["Entretenimiento", "Tendencias Digitales"],
            evidence_video_url=evidence_url,
            evidence_sha256=evidence_sha256,
            timestamp_utc=timestamp_utc
        ),
        demographics=DemographicsReport(
            sample_size=len(comments),
            age_distribution_percent=nlp_results["age_distribution_percent"],
            psychometrics_big_five=nlp_results["big_five_scores"],
            aqs_score=aqs_data["aqs_score"],
            dominant_emotion=nlp_results["dominant_emotion"],
            differential_privacy_epsilon=nlp_engine.dp_engine.epsilon
        ),
        risk_assessment=RiskAssessmentReport(
            risk_score=ai_verdict.get("risk_score", 50),
            risk_level=ai_verdict.get("risk_level", "MODERADO"),
            brand_safety_eligible=ai_verdict.get("brand_safety_eligible", False),
            parental_alert_triggered=ai_verdict.get("parental_alert_triggered", True),
            veredicto_etario=ai_verdict.get("veredicto_etario", ""),
            implicaciones_parentales=ai_verdict.get("implicaciones_parentales", ""),
            dictamen_brand_safety=ai_verdict.get("dictamen_brand_safety", ""),
            executive_conclusion=ai_verdict.get("conclusion_narrativa_global", ""),
            compliance_certification=ai_verdict.get("garantia_legal_lopdp", "Procesado conforme a LOPDP Arts. 19 y 21 con SHA-256 y ε-DP.")
        ),
        raw_anonymized_comments_count=len(comments)
    )

    return response_payload


@app.get("/api/v1/evidence/{filename}")
def download_evidence_file(filename: str):
    """Permite la descarga o visualización de la copia forense del archivo multimedia."""
    safe_filename = Path(filename).name
    file_path = EVIDENCE_DIR / safe_filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo de evidencia no encontrado.")
    return FileResponse(path=file_path, media_type="video/mp4", filename=safe_filename)
