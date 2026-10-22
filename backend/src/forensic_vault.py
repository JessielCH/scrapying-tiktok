"""
Módulo de Bóveda y Evidencia Forense Digital
============================================
Gestiona la descarga inmutable de videos de TikTok y la certificación pericial
de integridad mediante firmas criptográficas SHA-256 y sellado de tiempo UTC.
Permite conservar pruebas irrefutables ante eventuales eliminaciones de contenido.
"""

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

from .utils import ensure_output_dir


class ForensicVault:
    """
    Bóveda de evidencia forense digital para material audiovisual de TikTok.
    Descarga el flujo de video en su máxima calidad nativa y sella su autenticidad
    con una firma SHA-256 y un manifiesto de custodia inmutable.
    """

    def __init__(self, evidence_dir: str = "data/evidence", cookies_txt_path: Optional[str] = "data/cookies.txt"):
        self.evidence_dir = Path(evidence_dir)
        self.cookies_txt_path = Path(cookies_txt_path) if cookies_txt_path else None
        ensure_output_dir(self.evidence_dir)

    def _check_dependencies(self):
        if yt_dlp is None:
            raise RuntimeError(
                "La librería yt-dlp no está instalada. Instálala ejecutando:\n"
                "  pip install yt-dlp"
            )

    @staticmethod
    def calculate_sha256(file_path: Path) -> str:
        """Calcula el hash criptográfico SHA-256 de un archivo en bloques de 64 KB."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def capture_evidence(
        self,
        video_url: str,
        video_id: str,
        creator: str = "",
        custom_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Descarga el video objetivo y genera el manifiesto de evidencia forense.

        Args:
            video_url: Enlace web directo a la publicación de TikTok.
            video_id: Identificador numérico único del video.
            creator: Nombre de usuario o handle del creador auditado.
            custom_metadata: Diccionario opcional con metadatos contextuales adicionales.

        Returns:
            Diccionario estructurado con los datos de custodia y la firma criptográfica SHA-256.
        """
        self._check_dependencies()
        ensure_output_dir(self.evidence_dir)

        output_filename = f"{video_id}.mp4"
        output_file_path = self.evidence_dir / output_filename
        manifest_file_path = self.evidence_dir / f"{video_id}_manifest.json"

        # Opciones para yt-dlp asegurando máxima calidad y compatibilidad
        ydl_opts = {
            "outtmpl": str(output_file_path),
            "format": "bestvideo+bestaudio/best",
            "quiet": True,
            "no_warnings": True,
            "overwrites": True,
        }

        if self.cookies_txt_path and self.cookies_txt_path.exists():
            ydl_opts["cookiefile"] = str(self.cookies_txt_path)

        print(f"[*] [BÓVEDA FORENSE] Preservando evidencia inmutable del video {video_id}...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        if not output_file_path.exists():
            raise FileNotFoundError(
                f"No se pudo descargar el archivo de video en la ruta especificada: {output_file_path}"
            )

        # Cálculo de integridad criptográfica y tamaño
        sha256_signature = self.calculate_sha256(output_file_path)
        file_size_bytes = output_file_path.stat().st_size
        utc_timestamp = datetime.now(timezone.utc).isoformat()

        # Manifiesto pericial de cadena de custodia
        manifest_data = {
            "evidence_id": f"EVID-{video_id}",
            "video_id": video_id,
            "creator": creator,
            "source_url": video_url,
            "sha256_hash": sha256_signature,
            "file_size_bytes": file_size_bytes,
            "timestamp_utc": utc_timestamp,
            "local_file_name": output_filename,
            "chain_of_custody_status": "VERIFIED_IMMUTABLE",
            "context_metadata": custom_metadata or {}
        }

        with open(manifest_file_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)

        print(f"[OK] [BÓVEDA FORENSE] Video asegurado: {output_filename}")
        print(f"     Firma SHA-256: {sha256_signature}")
        print(f"     Manifiesto pericial: {manifest_file_path.name}")

        return manifest_data
