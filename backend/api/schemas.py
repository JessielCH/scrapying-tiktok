"""
Esquemas Pydantic para la API REST de Auditoría y Psicometría
==============================================================
Define los contratos de datos y validaciones para las solicitudes y respuestas.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class AuditRequest(BaseModel):
    """Solicitud de auditoría demográfica y psicométrica."""
    url: str = Field(..., description="URL del video o perfil de TikTok a auditar")
    sample_comments: int = Field(default=150, ge=10, le=1000, description="Número de comentarios a extraer y anonimizar")
    download_evidence: bool = Field(default=True, description="Descarga y preservación de evidencia forense inmutable con SHA-256")
    headed_browser: bool = Field(default=False, description="Abre el navegador en modo visible para resolución interactiva de captchas")


class TargetMetadata(BaseModel):
    url: str
    creator: str
    video_id: str
    categories: List[str]
    evidence_video_url: Optional[str] = None
    evidence_sha256: Optional[str] = None
    timestamp_utc: str


class DemographicsReport(BaseModel):
    sample_size: int
    age_distribution_percent: Dict[str, float]
    psychometrics_big_five: Dict[str, float]
    aqs_score: float
    dominant_emotion: str
    differential_privacy_epsilon: float


class RiskAssessmentReport(BaseModel):
    risk_score: int
    risk_level: str
    brand_safety_eligible: bool
    parental_alert_triggered: bool
    veredicto_etario: str
    implicaciones_parentales: str
    dictamen_brand_safety: str
    executive_conclusion: str
    compliance_certification: str


class CreatorProfile(BaseModel):
    """Perfil público y metadatos del creador auditado."""
    handle: str
    nickname: str
    bio: str
    avatar_url: Optional[str] = None
    verified: bool = False
    followers_count: Optional[str] = None
    likes_count: Optional[str] = None


class CategorizedComment(BaseModel):
    """Comentario individual anonimizado categorizado bajo el modelo Big Five."""
    comment_id: str
    author_hash: str
    text: str
    likes: int = 0
    primary_trait: str
    trait_key: str
    trait_icon: str
    explanation: str
    emotion: str


class AuditResponse(BaseModel):
    """Respuesta unificada de auditoría técnica devuelta al Frontend."""
    success: bool
    target: TargetMetadata
    creator_profile: Optional[CreatorProfile] = None
    demographics: DemographicsReport
    risk_assessment: RiskAssessmentReport
    comments_sample: List[CategorizedComment] = []
    big_five_breakdown: Dict[str, int] = {}
    raw_anonymized_comments_count: int
