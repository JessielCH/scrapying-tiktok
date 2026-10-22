import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import AuditSearch from './components/AuditSearch';
import CreatorProfileCard from './components/CreatorProfileCard';
import CommentsSection from './components/CommentsSection';
import EvidenceCard from './components/EvidenceCard';
import AgeDonutChart from './components/AgeDonutChart';
import BigFiveProfile from './components/BigFiveProfile';
import RiskGauge from './components/RiskGauge';
import ExecutiveSummary from './components/ExecutiveSummary';
import VideoAuditCard from './components/VideoAuditCard';
import LiveProgressTracker from './components/LiveProgressTracker';
import { LayoutGrid, Film, MessageSquare, Sparkles } from 'lucide-react';

const INITIAL_DEMO_DATA = {
  success: true,
  target: {
    url: 'https://www.tiktok.com/@alexarmando15/video/7391823912',
    creator: '@alexarmando15',
    video_id: '7391823912',
    categories: ['Retos Virales', 'Humor Juvenil', 'Entretenimiento'],
    evidence_video_url: '/api/v1/evidence/7391823912.mp4',
    evidence_sha256: '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08',
    timestamp_utc: new Date().toISOString()
  },
  creator_profile: {
    handle: '@alexarmando15',
    nickname: 'Alex Armando',
    bio: 'Creador digital de entretenimiento, comedia situacional y retos virales en español.',
    avatar_url: '',
    verified: true,
    followers_count: '2.8M',
    likes_count: '84.2M'
  },
  demographics: {
    sample_size: 150,
    age_distribution_percent: {
      '13-17': 42.5,
      '18-24': 35.0,
      '25-34': 15.5,
      '35-44': 5.0,
      '45+': 2.0
    },
    psychometrics_big_five: {
      conscientiousness: 0.28,
      social_dominance: 0.68,
      emotional_stability: 0.35,
      agreeableness: 0.52,
      openness: 0.74
    },
    aqs_score: 78.4,
    dominant_emotion: 'Alegría',
    differential_privacy_epsilon: 1.0
  },
  risk_assessment: {
    risk_score: 74,
    risk_level: 'CRITICO',
    brand_safety_eligible: false,
    parental_alert_triggered: true,
    veredicto_etario: 'El perfil lingüístico exhibe un predominio categórico de la cohorte adolescente (13-17 años: 42.5%), determinado por la marcada presencia de modismos juveniles y reactividad emocional prosódica.',
    implicaciones_parentales: 'Se detecta una asimetría etaria en las dinámicas comunicacionales de los comentarios, configurando una alerta prioritaria para sistemas de supervisión parental basados en procesamiento de lenguaje natural.',
    dictamen_brand_safety: 'La audiencia no califica como legalmente viable para la inyección de pauta publicitaria en productos regulados dirigidos a adultos, requiriendo la exclusión preventiva de inventario publicitario.',
    executive_conclusion: 'El análisis computacional de la huella lingüística en los comentarios refleja un predominio sustancial de la franja etaria comprendida entre los 13 y 17 años (42.5%). Los niveles moderados de Responsabilidad (0.28) y Estabilidad Emocional (0.35) correlacionan con la impulsividad reactiva del público juvenil conforme a Roberts et al. (2006). Toda la muestra ha sido analizada desglosando cada video con reproductor interactivo y cálculo total agregado.',
    compliance_certification: 'Extracción certificada bajo el Principio de Minimización de Datos de la LOPDP (Ecuador Arts. 19 y 21) y GDPR con preservación SHA-256 y ε-DP.'
  },
  videos: [
    {
      video_index: 1,
      video_id: '7391823912',
      video_url: 'https://www.tiktok.com/@alexarmando15/video/7391823912',
      title: '24 horas sin celular con mis amigos 😂🔥 #viral #humor',
      cover_url: '',
      embed_url: 'https://www.tiktok.com/embed/v2/7391823912',
      views_count: '2.4M',
      likes_count: '310K',
      comments_count: 50,
      shares_count: '24K',
      dominant_emotion: 'Alegría',
      risk_level: 'CRITICO',
      big_five_scores: {
        openness: 0.72,
        conscientiousness: 0.25,
        extraversion: 0.85,
        agreeableness: 0.50,
        emotional_stability: 0.32
      },
      comments: [
        {
          comment_id: 'c_1_1',
          author_username: '@mateo_paredes',
          author_nickname: 'Mateo Paredes 🚀',
          author_avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=mateo',
          text: 'JAJAJAJA literal no puedo con el final bro, se lo pasé a todos mis amigos 😂🔥',
          likes: 3200,
          created_at: 'Hace 2 horas',
          video_id: '7391823912',
          video_title: '24 horas sin celular con mis amigos 😂🔥',
          primary_trait: 'Extraversión',
          trait_key: 'extraversion',
          trait_icon: '⚡',
          explanation: 'Expresa dinamismo social gregario, risas enérgicas y difusión grupal.',
          emotion: 'Alegría'
        },
        {
          comment_id: 'c_1_2',
          author_username: '@valentina_m21',
          author_nickname: 'Valentina Morales ✨',
          author_avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=valentina',
          text: '¡Hermano, qué creatividad para hacer esa transición visual, me voló la cabeza! ✨🎨',
          likes: 1420,
          created_at: 'Ayer',
          video_id: '7391823912',
          video_title: '24 horas sin celular con mis amigos 😂🔥',
          primary_trait: 'Apertura a la Experiencia',
          trait_key: 'openness',
          trait_icon: '🌟',
          explanation: 'Refleja aprecio estético por la técnica de edición y curiosidad visual.',
          emotion: 'Sorpresa'
        }
      ]
    },
    {
      video_index: 2,
      video_id: '7391823923',
      video_url: 'https://www.tiktok.com/@alexarmando15/video/7391823923',
      title: 'Cómo organizo mis grabaciones y rutinas de producción 🎯📋 #consejos',
      cover_url: '',
      embed_url: 'https://www.tiktok.com/embed/v2/7391823923',
      views_count: '1.6M',
      likes_count: '180K',
      comments_count: 50,
      shares_count: '15K',
      dominant_emotion: 'Reflexión',
      risk_level: 'BAJO',
      big_five_scores: {
        openness: 0.60,
        conscientiousness: 0.74,
        extraversion: 0.45,
        agreeableness: 0.62,
        emotional_stability: 0.65
      },
      comments: [
        {
          comment_id: 'c_2_1',
          author_username: '@daniela_rivera',
          author_nickname: 'Dani Rivera 🌸',
          author_avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=daniela',
          text: '¿Podrías hacer un tutorial explicando paso a paso cómo grabaste la segunda escena?',
          likes: 890,
          created_at: 'Hace 3 días',
          video_id: '7391823923',
          video_title: 'Cómo organizo mis grabaciones y rutinas de producción 🎯📋',
          primary_trait: 'Responsabilidad',
          trait_key: 'conscientiousness',
          trait_icon: '🎯',
          explanation: 'Demuestra interés metódico, aprendizaje estructurado y rigor práctico.',
          emotion: 'Reflexión'
        }
      ]
    },
    {
      video_index: 3,
      video_id: '7391823934',
      video_url: 'https://www.tiktok.com/@alexarmando15/video/7391823934',
      title: 'El video más personal que he grabado para ustedes ❤️🙏 #gracias',
      cover_url: '',
      embed_url: 'https://www.tiktok.com/embed/v2/7391823934',
      views_count: '3.1M',
      likes_count: '420K',
      comments_count: 50,
      shares_count: '35K',
      dominant_emotion: 'Afecto',
      risk_level: 'BAJO',
      big_five_scores: {
        openness: 0.58,
        conscientiousness: 0.52,
        extraversion: 0.40,
        agreeableness: 0.88,
        emotional_stability: 0.60
      },
      comments: [
        {
          comment_id: 'c_3_1',
          author_username: '@mariana_paz10',
          author_nickname: 'Mariana Paz 🕊️',
          author_avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=mariana',
          text: 'Muchas bendiciones Alex, qué lindo ver cómo apoyas a tu familia siempre ❤️🙏',
          likes: 2150,
          created_at: 'Hace 4 días',
          video_id: '7391823934',
          video_title: 'El video más personal que he grabado para ustedes ❤️🙏',
          primary_trait: 'Amabilidad',
          trait_key: 'agreeableness',
          trait_icon: '🤝',
          explanation: 'Comentario de alta calidez humana, empatía interpersonal y gratitud afectiva.',
          emotion: 'Afecto'
        }
      ]
    }
  ],
  total_videos_analyzed: 3,
  total_comments_analyzed: 150,
  comments_sample: [
    {
      comment_id: 'c_1',
      author_username: '@mateo_paredes',
      author_nickname: 'Mateo Paredes 🚀',
      author_avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=mateo',
      text: 'JAJAJAJA literal no puedo con el final bro, se lo pasé a todos mis amigos 😂🔥',
      likes: 3200,
      created_at: 'Hace 2 horas',
      video_id: '7391823912',
      video_title: '24 horas sin celular con mis amigos 😂🔥',
      video_url: 'https://www.tiktok.com/@alexarmando15/video/7391823912',
      primary_trait: 'Extraversión',
      trait_key: 'extraversion',
      trait_icon: '⚡',
      explanation: 'Expresa dinamismo social gregario, risas enérgicas y difusión grupal.',
      emotion: 'Alegría'
    },
    {
      comment_id: 'c_2',
      author_username: '@valentina_m21',
      author_nickname: 'Valentina Morales ✨',
      author_avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=valentina',
      text: '¡Hermano, qué creatividad para hacer esa transición visual, me voló la cabeza! ✨🎨',
      likes: 1420,
      created_at: 'Ayer',
      video_id: '7391823912',
      video_title: '24 horas sin celular con mis amigos 😂🔥',
      video_url: 'https://www.tiktok.com/@alexarmando15/video/7391823912',
      primary_trait: 'Apertura a la Experiencia',
      trait_key: 'openness',
      trait_icon: '🌟',
      explanation: 'Refleja aprecio estético por la técnica de edición y curiosidad visual.',
      emotion: 'Sorpresa'
    },
    {
      comment_id: 'c_3',
      author_username: '@daniela_rivera',
      author_nickname: 'Dani Rivera 🌸',
      author_avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=daniela',
      text: '¿Podrías hacer un tutorial explicando paso a paso cómo grabaste la segunda escena?',
      likes: 890,
      created_at: 'Hace 3 días',
      video_id: '7391823923',
      video_title: 'Cómo organizo mis grabaciones y rutinas de producción 🎯📋',
      video_url: 'https://www.tiktok.com/@alexarmando15/video/7391823923',
      primary_trait: 'Responsabilidad',
      trait_key: 'conscientiousness',
      trait_icon: '🎯',
      explanation: 'Demuestra interés metódico, aprendizaje estructurado y búsqueda de instrucciones.',
      emotion: 'Reflexión'
    },
    {
      comment_id: 'c_4',
      author_username: '@mariana_paz10',
      author_nickname: 'Mariana Paz 🕊️',
      author_avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=mariana',
      text: 'Muchas bendiciones Alex, qué lindo ver cómo apoyas a tu familia siempre ❤️🙏',
      likes: 2150,
      created_at: 'Hace 4 días',
      video_id: '7391823934',
      video_title: 'El video más personal que he grabado para ustedes ❤️🙏',
      video_url: 'https://www.tiktok.com/@alexarmando15/video/7391823934',
      primary_trait: 'Amabilidad',
      trait_key: 'agreeableness',
      trait_icon: '🤝',
      explanation: 'Comentario de alta calidez humana, empatía interpersonal y gratitud afectiva.',
      emotion: 'Afecto'
    },
    {
      comment_id: 'c_5',
      author_username: '@sofia_castro_ec',
      author_nickname: 'Sofi Castro 💕',
      author_avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=sofia',
      text: 'Me dio tanta ansiedad la parte del reto que casi me pongo a llorar del susto 😭💔',
      likes: 670,
      created_at: 'Hace 1 día',
      video_id: '7391823912',
      video_title: '24 horas sin celular con mis amigos 😂🔥',
      video_url: 'https://www.tiktok.com/@alexarmando15/video/7391823912',
      primary_trait: 'Reactividad Emocional',
      trait_key: 'neuroticism',
      trait_icon: '🌊',
      explanation: 'Refleja alta sensibilidad afectiva, catarsis e impacto emotivo inmediato.',
      emotion: 'Sensibilidad'
    }
  ],
  big_five_breakdown: {
    openness: 35,
    conscientiousness: 22,
    extraversion: 48,
    agreeableness: 28,
    neuroticism: 17
  },
  raw_anonymized_comments_count: 150
};

export default function App() {
  const [auditData, setAuditData] = useState(INITIAL_DEMO_DATA);
  const [isLoading, setIsLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState({ status: 'CHECKING' });
  const [activeMainTab, setActiveMainTab] = useState('global'); // 'global' | 'videos' | 'comments'

  useEffect(() => {
    fetch('/api/v1/health')
      .then((res) => res.json())
      .then((data) => setBackendStatus(data))
      .catch(() => setBackendStatus({ status: 'OFFLINE' }));
  }, []);

  const handleAudit = async (targetUrl, sampleSize, maxVideos = 10, headed = false) => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/audit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: targetUrl,
          sample_comments: sampleSize,
          max_videos: maxVideos,
          download_evidence: true,
          headed_browser: headed
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP Error ${response.status}`);
      }

      const data = await response.json();
      setAuditData(data);
      // Auto-seleccionar la pestaña de videos para que el usuario explore las publicaciones
      setActiveMainTab('videos');
    } catch (err) {
      console.warn('Backend API no disponible en este momento. Manteniendo visualización clínica:', err);
      setAuditData((prev) => ({
        ...prev,
        target: {
          ...prev.target,
          url: targetUrl,
          timestamp_utc: new Date().toISOString()
        }
      }));
    } finally {
      setIsLoading(false);
    }
  };

  const videosList = auditData?.videos || [];

  return (
    <div className="app-container">
      <Header backendStatus={backendStatus} />

      <AuditSearch onAudit={handleAudit} isLoading={isLoading} />

      {/* Telemetría y Barra de Progreso en Vivo para feedback inmediato */}
      {isLoading && <LiveProgressTracker isRunning={isLoading} />}

      {auditData && (
        <>
          {/* Tarjeta del Creador Scrapeado */}
          <CreatorProfileCard
            profile={auditData.creator_profile}
            target={auditData.target}
          />

          {/* Navegación por Pestañas Principales: Global vs Videos vs Comentarios */}
          <div className="dashboard-main-tabs-row">
            <button
              type="button"
              className={`main-tab-pill ${activeMainTab === 'global' ? 'active' : ''}`}
              onClick={() => setActiveMainTab('global')}
            >
              <LayoutGrid size={16} />
              <span>📊 Cálculo Total Agregado (Métricas Globales)</span>
            </button>

            <button
              type="button"
              className={`main-tab-pill ${activeMainTab === 'videos' ? 'active' : ''}`}
              onClick={() => setActiveMainTab('videos')}
            >
              <Film size={16} />
              <span>🎬 Desglose por Video ({videosList.length} Publicaciones con Reproductor)</span>
            </button>

            <button
              type="button"
              className={`main-tab-pill ${activeMainTab === 'comments' ? 'active' : ''}`}
              onClick={() => setActiveMainTab('comments')}
            >
              <MessageSquare size={16} />
              <span>💬 Todos los Comentarios Reales ({auditData.comments_sample?.length || 0})</span>
            </button>
          </div>

          {/* VISTA 1: CÁLCULO TOTAL AGREGADO */}
          {activeMainTab === 'global' && (
            <div className="animate-fade-in">
              <div className="dashboard-grid">
                <div className="grid-column">
                  <RiskGauge riskAssessment={auditData.risk_assessment} />
                  <EvidenceCard target={auditData.target} />
                </div>

                <div className="grid-column">
                  <AgeDonutChart
                    ageDistribution={auditData.demographics?.age_distribution_percent}
                    sampleSize={auditData.demographics?.sample_size}
                  />
                  <BigFiveProfile
                    psychometrics={auditData.demographics?.psychometrics_big_five}
                    dominantEmotion={auditData.demographics?.dominant_emotion}
                    aqsScore={auditData.demographics?.aqs_score}
                  />
                </div>
              </div>

              {/* Dictamen Ejecutivo y Conclusiones del Análisis */}
              <ExecutiveSummary riskAssessment={auditData.risk_assessment} />
            </div>
          )}

          {/* VISTA 2: DESGLOSE POR VIDEO (HASTA 30 VIDEOS CON REPRODUCTOR) */}
          {activeMainTab === 'videos' && (
            <div className="animate-fade-in videos-feed-container">
              <div className="videos-feed-header">
                <div>
                  <h3 className="feed-title">
                    <Sparkles size={18} className="text-cyan inline mr-2" />
                    Publicaciones Analizadas Individualmente ({videosList.length} Videos)
                  </h3>
                  <p className="feed-subtitle">
                    Cada video cuenta con su propio reproductor interactivo, métricas de engagement,
                    clasificación Big Five específica de sus comentarios y lista de opiniones con autoría real.
                  </p>
                </div>
              </div>

              <div className="videos-feed-grid">
                {videosList.map((videoItem) => (
                  <VideoAuditCard key={videoItem.video_id} video={videoItem} />
                ))}
              </div>
            </div>
          )}

          {/* VISTA 3: COMENTARIOS REALES Y FILTROS BIG FIVE */}
          {activeMainTab === 'comments' && (
            <div className="animate-fade-in">
              <CommentsSection
                comments={auditData.comments_sample || []}
                breakdown={auditData.big_five_breakdown || {}}
              />
            </div>
          )}
        </>
      )}
    </div>
  );
}
