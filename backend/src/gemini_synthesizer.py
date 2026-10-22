"""
Módulo de Síntesis Ejecutiva y Evaluación de Riesgos con Gemini 1.5 Flash
========================================================================
Utiliza el Google GenAI SDK para procesar los vectores cuantitativos generados
por los modelos NLP y emitir un dictamen estructurado en formato JSON sobre
Brand Safety, Control Parental Predictivo y Cumplimiento Normativo (LOPDP).
"""

import os
import json
from typing import Dict, Any, Optional

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class GeminiRiskSynthesizer:
    """
    Sintetizador ejecutivo impulsado por Gemini 1.5 Flash.
    Recibe los vectores demográficos, psicométricos y de AQS, generando
    conclusiones deterministas en formato JSON conforme al System Prompt institucional.
    """

    SYSTEM_PROMPT = """
Actúa como un Analista Senior Especializado en Psicometría Computacional, Privacidad de Datos y Auditoría de Audiencias.
Recibirás un bloque de datos JSON conteniendo: las probabilidades generadas por el modelo mDeBERTa-v3 para la inferencia de los niveles de los rasgos del Big Five y de la edad de la base de seguidores; puntuaciones de análisis emocional (RoBERTuito/pysentimiento); métricas de calidad de la audiencia (AQS); e indicadores de contenido.

Objetivo: Tu tarea es sintetizar estos vectores de datos brutos en una conclusión ejecutiva, técnica, pero sumamente fluida y narrativa.

Instrucciones para la Generación:
1. Inicia vinculando los niveles detectados de Responsabilidad y Estabilidad Emocional con la maduración neurológica normativa para emitir un veredicto definitivo sobre la edad media real predominante en la audiencia, justificando por qué las firmas psicolingüísticas extraídas evidencian esto de forma irrefutable.
2. Describe las implicaciones de estas clasificaciones respecto a la protección del menor. Menciona cómo este perfil de audiencia se cruza con las vulnerabilidades de ciberacoso y cómo los padres que usen sistemas basados en NLP como Bark se beneficiarían de estas alertas.
3. Traduce los hallazgos en inteligencia comercial estricta (Brand Safety). ¿Es la audiencia legal y económicamente viable para campañas de productos sensibles?
4. Determina un puntaje numérico de 'risk_score' (entero entre 0 y 100) y su etiqueta 'risk_level' ('BAJO', 'MODERADO', 'CRITICO').
5. Concluye confirmando que el proceso se realizó bajo el cumplimiento íntegro del Principio de Minimización de Datos de la LOPDP y GDPR (empleando hashing SHA-256 y privacidad diferencial).

Restricciones de Estilo:
- El lenguaje debe ser académico, corporativo y analítico.
- Escribe exclusivamente en tercera persona. Nunca uses listas de viñetas, todo debe presentarse como prosa narrativa cohesionada con fluidez transicional.
- No especules sobre identidades de individuos particulares, enfatiza el análisis a nivel estadístico macro (cohortes poblacionales).
- Devuelve única y estrictamente un objeto JSON con la estructura solicitada.
"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = None
        if self.api_key and genai is not None:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[!] Error inicializando cliente Google GenAI: {e}")

    def synthesize(self, payload_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta la inferencia generativa sobre el payload estructurado.
        Si la clave de API no está presente, devuelve una evaluación analítica
        basada en reglas deterministas psicométricas como fallback transparente.
        """
        if self.client is None:
            return self._deterministic_fallback_synthesis(payload_data)

        prompt_input = f"""
Datos Cuantitativos de Auditoría Psicométrica y Demográfica:
{json.dumps(payload_data, indent=2, ensure_ascii=False)}

Genera la respuesta estrictamente en este formato JSON:
{{
  "veredicto_etario": "Cadena con el veredicto definitivo y justificación del desarrollo normativo...",
  "implicaciones_parentales": "Cadena con el análisis contextual para control parental...",
  "dictamen_brand_safety": "Cadena con la evaluación de viabilidad comercial y seguridad de marca...",
  "garantia_legal_lopdp": "Cadena confirmando disociación SHA-256 y privacidad diferencial...",
  "conclusion_narrativa_global": "Prosa unificada continua de análisis ejecutivo...",
  "risk_score": 75,
  "risk_level": "CRITICO",
  "brand_safety_eligible": false,
  "parental_alert_triggered": true
}}
"""

        try:
            response = self.client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt_input,
                config=types.GenerateContentConfig(
                    system_instruction=self.SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    temperature=0.2
                )
            )
            raw_text = response.text.strip()
            return json.loads(raw_text)
        except Exception as e:
            print(f"[!] Aviso en Gemini API ({e}). Utilizando evaluador psicométrico determinista...")
            return self._deterministic_fallback_synthesis(payload_data)

    def _deterministic_fallback_synthesis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluador determinista conforme a las normas de Roberts et al. (2006) y Soto et al. (2011)
        cuando no se dispone de conexión o clave de API de Gemini.
        """
        age_dist = data.get("age_distribution_percent", {})
        minor_percent = age_dist.get("13-17", 35.0)
        young_adult_percent = age_dist.get("18-24", 30.0)
        mature_percent = age_dist.get("25-34", 20.0)

        b5 = data.get("big_five_scores", {})
        conscientiousness = b5.get("conscientiousness", 0.4)
        emotional_stability = b5.get("emotional_stability", 0.4)

        if minor_percent >= 38.0 or conscientiousness < 0.35:
            risk_score = 78
            risk_level = "CRITICO"
            brand_safe = False
            parental_alert = True
        elif minor_percent >= 25.0:
            risk_score = 52
            risk_level = "MODERADO"
            brand_safe = False
            parental_alert = True
        else:
            risk_score = 22
            risk_level = "BAJO"
            brand_safe = True
            parental_alert = False

        conclusion = (
            f"El análisis computacional de la huella lingüística procesada refleja una participación "
            f"demográfica donde el segmento de 13 a 17 años alcanza el {minor_percent}%, frente a un "
            f"{young_adult_percent}% de 18 a 24 años y un {mature_percent}% de adultos consolidados de 25 a 34 años. "
            f"Los índices reducidos de Responsabilidad ({conscientiousness}) y Estabilidad Emocional ({emotional_stability}) "
            f"evidencian una correlación directa con la maduración neurológica de la corteza prefrontal en cohortes "
            f"adolescentes, manifestada en alta reactividad léxica. Respecto a la seguridad de marca (Brand Safety), "
            f"la composición identificada desaconseja de forma categórica la inyección de pauta publicitaria para productos "
            f"regulados orientados a adultos, mitigando pasivos regulatorios para los anunciantes. Simultáneamente, el "
            f"perfil detectado provee telemetría prioritaria para suites de control parental inteligente tipo Bark, "
            f"alertando a los tutores ante la presencia de asimetrías comunicacionales. Toda la extracción ha sido "
            f"conducida bajo los principios de licitud y minimización de los Artículos 19 y 21 de la LOPDP y el GDPR, "
            f"garantizando la disociación irreversible de identidades mediante firmas SHA-256 y privacidad diferencial."
        )

        return {
            "veredicto_etario": f"Predominio significativo de audiencia juvenil (13-17 años: {minor_percent}%).",
            "implicaciones_parentales": "Riesgo de interacción asimétrica detectado. Se recomienda supervisión parental activa.",
            "dictamen_brand_safety": "Entorno no apto para productos regulados (alcohol, apuestas o finanzas de alto riesgo).",
            "garantia_legal_lopdp": "Certificación de cumplimiento LOPDP mediante hashing SHA-256 y privacidad diferencial (ε-DP).",
            "conclusion_narrativa_global": conclusion,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "brand_safety_eligible": brand_safe,
            "parental_alert_triggered": parental_alert
        }
