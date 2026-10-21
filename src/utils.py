"""
Módulo de Utilidades del Sistema
==================================
Funciones auxiliares para gestión de directorios, serialización de cookies
y exportación de datos tabulares a formatos CSV y JSON compatibles con pandas.
"""

import csv
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


def ensure_output_dir(dir_path: Path) -> Path:
    """Garantiza la existencia del directorio de destino y retorna el objeto Path."""
    dir_path = Path(dir_path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def export_posts_to_csv(posts: List[Dict[str, Any]], output_file: Path, username: str = "", followers: int = 0) -> Path:
    """
    Exporta la lista de publicaciones (videos y carruseles) a formato CSV tabular
    compatible con pandas DataFrame, Excel y herramientas de análisis de datos.
    """
    output_file = Path(output_file)
    ensure_output_dir(output_file.parent)

    fieldnames = [
        "usuario",
        "seguidores",
        "id",
        "tipo",
        "descripcion",
        "likes",
        "comentarios",
        "guardados",
        "compartidos",
        "vistas",
        "fotos_carrusel",
        "fecha",
        "url"
    ]

    with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in posts:
            create_time = p.get("create_time", 0)
            fecha_str = ""
            if create_time:
                try:
                    fecha_str = datetime.fromtimestamp(int(create_time)).strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    fecha_str = str(create_time)

            writer.writerow({
                "usuario": username,
                "seguidores": followers,
                "id": p.get("id", ""),
                "tipo": p.get("type", "video"),
                "descripcion": p.get("description", "").replace("\n", " ").strip(),
                "likes": p.get("likes", 0),
                "comentarios": p.get("comments", 0),
                "guardados": p.get("saves", 0),
                "compartidos": p.get("shares", 0),
                "vistas": p.get("views", 0),
                "fotos_carrusel": p.get("carousel_images_count", 0),
                "fecha": fecha_str,
                "url": p.get("url", "")
            })

    return output_file


def export_summary_to_csv(report: Dict[str, Any], output_file: Path) -> Path:
    """
    Exporta el resumen completo del perfil y del analisis numerico de publicaciones
    a un archivo CSV estructurado (clave-valor con secciones) para analisis o visualizacion en Excel.
    """
    output_file = Path(output_file)
    ensure_output_dir(output_file.parent)

    profile = report.get("profile", {})
    p_analysis = report.get("posts_analysis", {})
    post_types = p_analysis.get("post_types", {})
    totals = p_analysis.get("metrics_totals", {})
    averages = p_analysis.get("metrics_averages", {})
    perf = p_analysis.get("performance", {})
    posts = p_analysis.get("posts", [])

    rows = [
        # Seccion Perfil
        {"seccion": "PERFIL", "metrica": "Usuario", "valor": profile.get("username", "")},
        {"seccion": "PERFIL", "metrica": "Nombre Visible", "valor": profile.get("nickname", "")},
        {"seccion": "PERFIL", "metrica": "Biografia", "valor": profile.get("biography", "")},
        {"seccion": "PERFIL", "metrica": "Cuenta Verificada", "valor": "Si" if profile.get("verified") else "No"},
        {"seccion": "PERFIL", "metrica": "Seguidos", "valor": profile.get("following_count", 0)},
        {"seccion": "PERFIL", "metrica": "Seguidores", "valor": profile.get("follower_count", 0)},
        {"seccion": "PERFIL", "metrica": "Total Likes Recibidos", "valor": profile.get("total_likes_received", 0)},
        {"seccion": "PERFIL", "metrica": "Total Videos Cuenta", "valor": profile.get("total_videos_count", 0)},

        # Seccion Analisis Numerico Totales
        {"seccion": "ANALISIS NUMERICO", "metrica": "Publicaciones Analizadas", "valor": len(posts)},
        {"seccion": "ANALISIS NUMERICO", "metrica": "Videos Analizados", "valor": post_types.get("videos_count", 0)},
        {"seccion": "ANALISIS NUMERICO", "metrica": "Carruseles Analizados", "valor": post_types.get("carousels_count", 0)},
        {"seccion": "ANALISIS NUMERICO", "metrica": "Fotos en Carruseles", "valor": post_types.get("total_carousel_images", 0)},
        {"seccion": "ANALISIS NUMERICO", "metrica": "Total Likes", "valor": totals.get("likes", 0)},
        {"seccion": "ANALISIS NUMERICO", "metrica": "Total Comentarios", "valor": totals.get("comments", 0)},
        {"seccion": "ANALISIS NUMERICO", "metrica": "Total Guardados (Favoritos)", "valor": totals.get("saves", 0)},
        {"seccion": "ANALISIS NUMERICO", "metrica": "Total Compartidos", "valor": totals.get("shares", 0)},
        {"seccion": "ANALISIS NUMERICO", "metrica": "Total Vistas", "valor": totals.get("views", 0)},
        {"seccion": "ANALISIS NUMERICO", "metrica": "Total Interacciones", "valor": totals.get("total_interactions", 0)},

        # Seccion Promedios y Rendimiento
        {"seccion": "PROMEDIOS Y RENDIMIENTO", "metrica": "Promedio Likes por Post", "valor": averages.get("avg_likes", 0)},
        {"seccion": "PROMEDIOS Y RENDIMIENTO", "metrica": "Promedio Comentarios por Post", "valor": averages.get("avg_comments", 0)},
        {"seccion": "PROMEDIOS Y RENDIMIENTO", "metrica": "Promedio Guardados por Post", "valor": averages.get("avg_saves", 0)},
        {"seccion": "PROMEDIOS Y RENDIMIENTO", "metrica": "Promedio Compartidos por Post", "valor": averages.get("avg_shares", 0)},
        {"seccion": "PROMEDIOS Y RENDIMIENTO", "metrica": "Promedio Vistas por Post", "valor": averages.get("avg_views", 0)},
        {"seccion": "PROMEDIOS Y RENDIMIENTO", "metrica": "Tasa Engagement", "valor": f"{perf.get('engagement_rate_percent', 0)}%"},
    ]

    with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["seccion", "metrica", "valor"])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    return output_file


def export_profile_to_csv(profile: Dict[str, Any], output_file: Path) -> Path:
    """
    Exporta el resumen del perfil a formato CSV tabular de una sola fila.
    """
    output_file = Path(output_file)
    ensure_output_dir(output_file.parent)

    fieldnames = list(profile.keys())

    with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(profile)

    return output_file


def export_to_netscape_format(cookies: List[Dict[str, Any]], output_file: Path):
    """
    Exporta la lista de cookies al formato estándar Netscape HTTP (cookies.txt).
    """
    output_file = Path(output_file)
    ensure_output_dir(output_file.parent)

    lines = [
        "# Netscape HTTP Cookie File",
        "# https://curl.se/docs/http-cookies.html",
        "# Generado automaticamente por el Gestor de Cookies de TikTok",
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
    Carga cookies desde formato JSON (Playwright) o formato Netscape (.txt).
    Retorna un diccionario de pares clave-valor para peticiones HTTP.
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
        print(f"[!] Aviso al leer cookies ({cookies_path}): {e}")
    return cookies
