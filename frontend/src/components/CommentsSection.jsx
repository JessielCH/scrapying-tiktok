import React, { useState, useMemo } from 'react';
import { Film, ExternalLink, Heart } from 'lucide-react';

const TRAITS_INFO = {
  all: {
    label: 'Todos los Comentarios',
    icon: '💬',
    desc: 'Muestra completa de comentarios públicos de la audiencia con autoría real, métricas y referencia de video.',
    color: '#0284c7'
  },
  openness: {
    label: 'Apertura a la Experiencia',
    icon: '🌟',
    desc: 'Comentarios que reflejan curiosidad intelectual, aprecio estético, arte, originalidad y preguntas creativas.',
    color: '#8b5cf6'
  },
  conscientiousness: {
    label: 'Responsabilidad',
    icon: '🎯',
    desc: 'Comentarios enfocados en consejos útiles, metodología, tutoriales, disciplina y recomendaciones ordenadas.',
    color: '#0ea5e9'
  },
  extraversion: {
    label: 'Extraversión',
    icon: '⚡',
    desc: 'Comentarios de alta energía festiva, humor social, risas intensas (jajaja, xd) y dinamismo grupal.',
    color: '#f59e0b'
  },
  agreeableness: {
    label: 'Amabilidad',
    icon: '🤝',
    desc: 'Comentarios de afecto sincero, empatía interpersonal, bendiciones, elogios y apoyo mutuo comunitario.',
    color: '#10b981'
  },
  neuroticism: {
    label: 'Reactividad Emocional',
    icon: '🌊',
    desc: 'Comentarios con alta carga afectiva, catarsis emocional, dudas existenciales o desahogo de tensiones.',
    color: '#ec4899'
  }
};

export default function CommentsSection({ comments = [], breakdown = {} }) {
  const [selectedTrait, setSelectedTrait] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [displayLimit, setDisplayLimit] = useState(12);

  const filteredComments = useMemo(() => {
    return comments.filter((c) => {
      const matchesTrait = selectedTrait === 'all' || c.trait_key === selectedTrait;
      const matchesSearch =
        !searchTerm.trim() ||
        c.text.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (c.author_username && c.author_username.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (c.author_nickname && c.author_nickname.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (c.primary_trait && c.primary_trait.toLowerCase().includes(searchTerm.toLowerCase()));
      return matchesTrait && matchesSearch;
    });
  }, [comments, selectedTrait, searchTerm]);

  const activeTraitInfo = TRAITS_INFO[selectedTrait] || TRAITS_INFO.all;

  const counts = {
    all: comments.length,
    openness: breakdown.openness || comments.filter((c) => c.trait_key === 'openness').length,
    conscientiousness: breakdown.conscientiousness || comments.filter((c) => c.trait_key === 'conscientiousness').length,
    extraversion: breakdown.extraversion || comments.filter((c) => c.trait_key === 'extraversion').length,
    agreeableness: breakdown.agreeableness || comments.filter((c) => c.trait_key === 'agreeableness').length,
    neuroticism: breakdown.neuroticism || comments.filter((c) => c.trait_key === 'neuroticism').length
  };

  return (
    <div className="card comments-section-card">
      <div className="comments-header">
        <div>
          <div className="section-badge-pill">Psicometría Computacional del Lenguaje</div>
          <h2 className="comments-title">Comentarios Reales de la Audiencia Desglosados por Big Five</h2>
          <p className="comments-subtitle">
            Mostrando usuarios reales, avatares, métricas y la publicación exacta de origen, clasificados
            bajo las 5 dimensiones fundamentales de la personalidad psicológica.
          </p>
        </div>

        <div className="comments-search-box">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <input
            type="text"
            placeholder="Buscar por usuario o palabra..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="comments-search-input"
          />
          {searchTerm && (
            <button className="clear-search-btn" onClick={() => setSearchTerm('')} title="Limpiar búsqueda">
              ×
            </button>
          )}
        </div>
      </div>

      {/* Pestañas de las 5 Dimensiones Big Five */}
      <div className="traits-tabs-row">
        {Object.entries(TRAITS_INFO).map(([key, info]) => {
          const isSelected = selectedTrait === key;
          const count = counts[key] || 0;

          return (
            <button
              key={key}
              type="button"
              className={`trait-tab-btn ${isSelected ? 'active' : ''}`}
              style={{
                borderColor: isSelected ? info.color : '#e2e8f0',
                backgroundColor: isSelected ? `${info.color}12` : '#ffffff',
                color: isSelected ? info.color : '#475569'
              }}
              onClick={() => {
                setSelectedTrait(key);
                setDisplayLimit(12);
              }}
            >
              <span className="trait-tab-icon">{info.icon}</span>
              <span className="trait-tab-name">{info.label}</span>
              <span className="trait-tab-count">{count}</span>
            </button>
          );
        })}
      </div>

      {/* Banner explicativo del rasgo seleccionado */}
      <div className="trait-explanation-banner" style={{ borderLeftColor: activeTraitInfo.color }}>
        <div className="banner-icon" style={{ backgroundColor: `${activeTraitInfo.color}15`, color: activeTraitInfo.color }}>
          {activeTraitInfo.icon}
        </div>
        <div className="banner-content">
          <h4 className="banner-title" style={{ color: activeTraitInfo.color }}>
            {activeTraitInfo.label} — ¿Qué significa esta dimensión?
          </h4>
          <p className="banner-desc">{activeTraitInfo.desc}</p>
        </div>
      </div>

      {/* Cuadrícula de comentarios con autoría real y video de origen */}
      {filteredComments.length === 0 ? (
        <div className="comments-empty-state">
          <div className="empty-icon">🔍</div>
          <p className="empty-title">No se encontraron comentarios para este filtro</p>
          <p className="empty-desc">
            Prueba seleccionando otra dimensión del Big Five o borrando el texto de búsqueda.
          </p>
        </div>
      ) : (
        <>
          <div className="comments-grid">
            {filteredComments.slice(0, displayLimit).map((c, idx) => (
              <div key={c.comment_id || idx} className="comment-card">
                {/* Cabecera con Autor Real */}
                <div className="comment-real-author-header">
                  <img
                    src={c.author_avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${c.author_username || idx}`}
                    alt={c.author_nickname}
                    className="author-avatar-img"
                    onError={(e) => {
                      e.target.src = `https://api.dicebear.com/7.x/avataaars/svg?seed=${idx}`;
                    }}
                  />
                  <div className="author-names">
                    <span className="author-display-name">{c.author_nickname || 'Usuario de TikTok'}</span>
                    <span className="author-handle-name">{c.author_username || '@usuario'}</span>
                  </div>
                  <span className="comment-time-pill">{c.created_at || 'Reciente'}</span>
                </div>

                {/* Referencia a la Publicación donde aparece */}
                {(c.video_title || c.video_id) && (
                  <div className="comment-video-origin" title={c.video_title || ''}>
                    <Film size={12} className="text-cyan shrink-0" />
                    <span className="video-origin-label">En video:</span>
                    <span className="video-origin-title">{c.video_title || `Video ID ${c.video_id}`}</span>
                    {c.video_url && (
                      <a
                        href={c.video_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="video-origin-link"
                        title="Ver video en TikTok"
                      >
                        <ExternalLink size={11} />
                      </a>
                    )}
                  </div>
                )}

                {/* Texto del Comentario */}
                <p className="comment-text">"{c.text}"</p>

                {/* Pie de Tarjeta con Dimensión Big Five y Likes */}
                <div className="comment-card-bottom">
                  <span
                    className="trait-pill"
                    style={{
                      backgroundColor: `${(TRAITS_INFO[c.trait_key] || TRAITS_INFO.all).color}15`,
                      color: (TRAITS_INFO[c.trait_key] || TRAITS_INFO.all).color
                    }}
                  >
                    <span>{c.trait_icon || '💬'}</span>
                    <span>{c.primary_trait}</span>
                  </span>

                  <div className="comment-likes" title={`${c.likes} me gusta`}>
                    <Heart size={13} className="text-rose" />
                    <span>{c.likes || 0}</span>
                  </div>
                </div>

                {/* Explicación Psicolingüística */}
                {c.explanation && (
                  <div className="comment-why" title="Fundamento psicolingüístico">
                    <span className="why-label">Interpretación:</span>
                    <span className="why-text">{c.explanation}</span>
                  </div>
                )}
              </div>
            ))}
          </div>

          {filteredComments.length > displayLimit && (
            <div className="load-more-comments-wrapper">
              <button
                className="btn-load-more"
                onClick={() => setDisplayLimit((prev) => prev + 12)}
              >
                Cargar Más Comentarios ({filteredComments.length - displayLimit} restantes)
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
