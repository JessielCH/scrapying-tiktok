"""
Módulo de Privacidad Diferencial y Auditoría de Audiencia (AQS)
================================================================
Implementa garantías matemáticas formales de Privacidad Diferencial (ε-DP)
mediante inyección de ruido Laplaciano sobre métricas agregadas de edad y personalidad,
además del algoritmo Audience Quality Score (AQS) para discernir interacciones genuinas.
"""

import re
import numpy as np
from typing import Dict, Any, List


class DifferentialPrivacyEngine:
    """
    Motor matemático de Privacidad Diferencial (ε-DP) para analítica de audiencias.
    Aplica el mecanismo de Laplace para asegurar que las distribuciones demográficas
    y psicométricas resultantes no permitan la reidentificación de ningún usuario particular.
    """

    def __init__(self, epsilon: float = 1.0):
        """
        Args:
            epsilon: Parámetro de presupuesto de privacidad (ε). Valores menores
                     aportan mayor privacidad a costa de ligera variación estocástica.
        """
        self.epsilon = max(0.1, float(epsilon))

    def add_laplace_noise(self, value: float, sensitivity: float = 1.0) -> float:
        """
        Inyecta ruido calibrado muestreado de una distribución Laplaciana:
        Noise ~ Laplace(0, sensitivity / epsilon).
        """
        scale = sensitivity / self.epsilon
        noise = np.random.laplace(0, scale)
        noisy_val = value + noise
        return max(0.0, float(noisy_val))

    def sanitize_distribution(self, distribution: Dict[str, float]) -> Dict[str, float]:
        """
        Aplica ruido Laplaciano a un histograma o diccionario de porcentajes
        y normaliza las frecuencias para que su suma matemática sea exactamente 100%.
        """
        noisy_counts = {}
        for category, count in distribution.items():
            noisy_counts[category] = self.add_laplace_noise(count, sensitivity=1.0)

        total_sum = sum(noisy_counts.values())
        if total_sum <= 0:
            return {cat: 0.0 for cat in distribution}

        # Normalización a 100% garantizada matemáticamente
        res = {
            cat: round((val / total_sum) * 100.0, 1)
            for cat, val in noisy_counts.items()
        }
        diff = round(100.0 - sum(res.values()), 1)
        if diff != 0:
            max_cat = max(res, key=res.get)
            res[max_cat] = round(res[max_cat] + diff, 1)
        return res


class AudienceQualityAnalyzer:
    """
    Calcula el Audience Quality Score (AQS de 1 a 100) y extrae marcadores
    psicolingüísticos de los comentarios (longitud media, densidad de emojis y jerga).
    """

    GENERIC_PATTERNS = [
        r"^(nice|cool|great|wow|hello|hi|bueno|lindo|hermoso|genial|ok|uwu)$",
        r"^([\U00010000-\U0010ffff\s]{1,4})$",  # Comentarios de solo 1 a 4 emojis
        r"(follow me|sigueme|dale like|sub x sub|x2|x3)"
    ]

    @classmethod
    def calculate_aqs_and_markers(
        cls,
        comments: List[Dict[str, Any]],
        engagement_rate: float = 5.0
    ) -> Dict[str, Any]:
        """
        Evalúa la autenticidad lingüística de los comentarios y computa el AQS.
        """
        total = len(comments)
        if total == 0:
            return {
                "aqs_score": 0.0,
                "authenticity_percent": 0.0,
                "spam_bot_percent": 0.0,
                "avg_word_length": 0.0,
                "emoji_density": 0.0,
                "elongation_rate": 0.0
            }

        authentic_count = 0
        total_words = 0
        elongations = 0
        emoji_count = 0

        # Regex para detección de alargamiento vocálico (ej. siiiii, holaaaaa)
        elongation_regex = re.compile(r"([a-zA-ZáéíóúÁÉÍÓÚ])\1{2,}")
        emoji_regex = re.compile(r"[\U00010000-\U0010ffff]")

        for c in comments:
            text = c.get("text", "").strip().lower()
            words = text.split()
            total_words += len(words)

            if elongation_regex.search(text):
                elongations += 1

            emojis_found = len(emoji_regex.findall(text))
            emoji_count += emojis_found

            # Comprobar si coincide con patrones genéricos o granjas de bots
            is_generic = any(re.search(pat, text) for pat in cls.GENERIC_PATTERNS)
            if not is_generic and len(words) >= 2:
                authentic_count += 1

        authenticity_percent = round((authentic_count / total) * 100.0, 2)
        spam_bot_percent = round(100.0 - authenticity_percent, 2)
        avg_word_length = round(total_words / total, 2) if total > 0 else 0.0
        emoji_density = round(emoji_count / total, 2) if total > 0 else 0.0
        elongation_rate = round((elongations / total) * 100.0, 2) if total > 0 else 0.0

        # Algoritmo sintético de AQS (1 a 100) ponderando engagement y autenticidad
        # Pilar 1: Autenticidad (60%), Pilar 2: Tasa de Interacción (25%), Pilar 3: Riqueza léxica (15%)
        er_norm = min(100.0, engagement_rate * 10.0)
        lexical_norm = min(100.0, avg_word_length * 10.0)
        raw_aqs = (authenticity_percent * 0.60) + (er_norm * 0.25) + (lexical_norm * 0.15)
        final_aqs = round(max(1.0, min(100.0, raw_aqs)), 1)

        return {
            "aqs_score": final_aqs,
            "authenticity_percent": authenticity_percent,
            "spam_bot_percent": spam_bot_percent,
            "avg_word_length": avg_word_length,
            "emoji_density": emoji_density,
            "elongation_rate": elongation_rate
        }
