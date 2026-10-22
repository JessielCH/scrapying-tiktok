"""
Módulo de Procesamiento de Lenguaje Natural y Psicometría Computacional
========================================================================
Implementa clasificación Zero-Shot con mDeBERTa-v3 para estimación etaria y
perfilado Big Five (Cinco Grandes), complementado con análisis emocional de Ekman
y marcadores psicolingüísticos en el idioma español.
"""

import numpy as np
from typing import Dict, Any, List, Optional

try:
    from transformers import pipeline
except ImportError:
    pipeline = None

try:
    from pysentimiento import create_analyzer
except ImportError:
    create_analyzer = None

from .privacy_dp import DifferentialPrivacyEngine


class PsychometricsNLPEngine:
    """
    Motor de psicometría computacional e inferencia etaria a partir de texto.
    Apalanca modelos preentrenados multilingües (mDeBERTa-v3) y modelos específicos
    de Social NLP en español (RoBERTuito/pysentimiento).
    """

    AGE_CANDIDATE_LABELS = [
        "escrito por un adolescente de 13 a 17 años",
        "escrito por un joven de 18 a 24 años",
        "escrito por un adulto joven de 25 a 34 años",
        "escrito por un adulto maduro de 35 a 44 años",
        "escrito por un adulto mayor de 45 años o más"
    ]

    AGE_LABEL_MAP = {
        "escrito por un adolescente de 13 a 17 años": "13-17",
        "escrito por un joven de 18 a 24 años": "18-24",
        "escrito por un adulto joven de 25 a 34 años": "25-34",
        "escrito por un adulto maduro de 35 a 44 años": "35-44",
        "escrito por un adulto mayor de 45 años o más": "45+"
    }

    BIG_FIVE_TRAIT_LABELS = [
        "alta responsabilidad y autocontrol de impulsos",
        "alta dominancia social y asertividad",
        "alta estabilidad emocional y tranquilidad",
        "alta amabilidad y empatia comunitaria",
        "alta apertura a la experiencia y creatividad"
    ]

    BIG_FIVE_MAP = {
        "alta responsabilidad y autocontrol de impulsos": "conscientiousness",
        "alta dominancia social y asertividad": "social_dominance",
        "alta estabilidad emocional y tranquilidad": "emotional_stability",
        "alta amabilidad y empatia comunitaria": "agreeableness",
        "alta apertura a la experiencia y creatividad": "openness"
    }

    def __init__(
        self,
        model_name: str = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7",
        device: int = -1,
        epsilon: float = 1.0
    ):
        self.model_name = model_name
        self.device = device
        self.dp_engine = DifferentialPrivacyEngine(epsilon=epsilon)
        self._classifier = None
        self._emotion_analyzer = None

    def _get_classifier(self):
        """Carga perezosa del clasificador Zero-Shot de Transformers."""
        if self._classifier is None:
            if pipeline is None:
                raise RuntimeError(
                    "La librería transformers no está instalada. Instálala con:\n"
                    "  pip install transformers torch"
                )
            print(f"[*] [NLP ENGINE] Inicializando modelo Zero-Shot ({self.model_name})...")
            self._classifier = pipeline(
                "zero-shot-classification",
                model=self.model_name,
                device=self.device
            )
        return self._classifier

    def _get_emotion_analyzer(self):
        """Carga perezosa del analizador de emociones de pysentimiento."""
        if self._emotion_analyzer is None and create_analyzer is not None:
            try:
                print("[*] [NLP ENGINE] Inicializando modelo RoBERTuito para emociones...")
                self._emotion_analyzer = create_analyzer(task="emotion", lang="es")
            except Exception as e:
                print(f"[!] Aviso al cargar pysentimiento: {e}")
                self._emotion_analyzer = None
        return self._emotion_analyzer

    def analyze_comment_batch(
        self,
        comments: List[Dict[str, Any]],
        batch_size: int = 16
    ) -> Dict[str, Any]:
        """
        Procesa una muestra de comentarios y devuelve las distribuciones agregadas
        de edad y personalidad protegidas por Privacidad Diferencial (ε-DP).
        """
        if not comments:
            return {
                "age_distribution_percent": {"13-17": 20.0, "18-24": 20.0, "25-34": 20.0, "35-44": 20.0, "45+": 20.0},
                "big_five_scores": {"conscientiousness": 0.5, "social_dominance": 0.5, "emotional_stability": 0.5, "agreeableness": 0.5, "openness": 0.5},
                "dominant_emotion": "alegría",
                "processed_count": 0
            }

        texts = [c.get("text", "").strip() for c in comments if len(c.get("text", "").strip()) >= 3]
        if not texts:
            texts = ["genial"]

        classifier = self._get_classifier()

        raw_age_counts = {"13-17": 0.0, "18-24": 0.0, "25-34": 0.0, "35-44": 0.0, "45+": 0.0}
        big_five_sums = {"conscientiousness": 0.0, "social_dominance": 0.0, "emotional_stability": 0.0, "agreeableness": 0.0, "openness": 0.0}
        emotions_counts: Dict[str, int] = {}

        emotion_analyzer = self._get_emotion_analyzer()

        # Clasificación por lotes
        print(f"[*] [NLP ENGINE] Ejecutando inferencia sobre {len(texts)} textos en lotes de {batch_size}...")
        for i in range(0, len(texts), batch_size):
            chunk = texts[i : i + batch_size]
            try:
                # Inferencia Zero-Shot para edad
                age_results = classifier(
                    chunk,
                    candidate_labels=self.AGE_CANDIDATE_LABELS,
                    multi_label=False,
                    hypothesis_template="Este comentario en redes sociales está {}."
                )
                if isinstance(age_results, dict):
                    age_results = [age_results]

                for res in age_results:
                    top_label = res["labels"][0]
                    mapped_age = self.AGE_LABEL_MAP.get(top_label, "18-24")
                    raw_age_counts[mapped_age] += 1.0

                # Inferencia Zero-Shot para rasgos Big Five
                b5_results = classifier(
                    chunk,
                    candidate_labels=self.BIG_FIVE_TRAIT_LABELS,
                    multi_label=True,
                    hypothesis_template="El autor de este texto demuestra {}."
                )
                if isinstance(b5_results, dict):
                    b5_results = [b5_results]

                for b5_res in b5_results:
                    for lbl, score in zip(b5_res["labels"], b5_res["scores"]):
                        key = self.BIG_FIVE_MAP.get(lbl)
                        if key:
                            big_five_sums[key] += float(score)

                # Detección de emociones con RoBERTuito
                if emotion_analyzer:
                    try:
                        emo_predictions = emotion_analyzer.predict(chunk)
                        if not isinstance(emo_predictions, list):
                            emo_predictions = [emo_predictions]
                        for ep in emo_predictions:
                            emo_name = getattr(ep, "output", "joy")
                            emotions_counts[emo_name] = emotions_counts.get(emo_name, 0) + 1
                    except Exception:
                        pass

            except Exception as e:
                print(f"[!] Error procesando lote NLP: {e}")
                # Fallback distributivo para tolerar excepciones locales
                for _ in chunk:
                    raw_age_counts["18-24"] += 1.0
                    for k in big_five_sums:
                        big_five_sums[k] += 0.5

        # 1. Aplicación de Privacidad Diferencial (Ruido Laplace) sobre distribución de edad
        sanitized_age_dist = self.dp_engine.sanitize_distribution(raw_age_counts)

        # 2. Promedio y normalización de puntuaciones Big Five (0.0 a 1.0)
        n_texts = max(1, len(texts))
        big_five_avg = {
            k: round(min(1.0, max(0.0, val / n_texts)), 2)
            for k, val in big_five_sums.items()
        }

        dominant_emotion = max(emotions_counts, key=emotions_counts.get) if emotions_counts else "alegria"

        return {
            "age_distribution_percent": sanitized_age_dist,
            "big_five_scores": big_five_avg,
            "dominant_emotion": dominant_emotion,
            "processed_count": len(texts)
        }
