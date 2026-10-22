import React, { useState, useMemo } from 'react';

const TRAITS_INFO = {
  all: {
    label: 'Todos los Comentarios',
    icon: '💬',
    desc: 'Muestra completa de comentarios públicos anonimizados en memoria mediante algoritmo SHA-256.',
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

  // Filtrado reactivo por rasgo y término de búsqueda
  const filteredComments = useMemo(() => {
    return comments.filter((c) => {
      const matchesTrait = selectedTrait === 'all' || c.trait_key === selectedTrait;
      const matchesSearch =
        !searchTerm.trim() ||
        c.text.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.primary_trait.toLowerCase().includes(searchTerm.toLowerCase());
      return matchesTrait && matchesSearch;
    });
  }, [comments, selectedTrait, searchTerm]);

  const activeTraitInfo = TRAITS_INFO[selectedTrait] || TRAITS_INFO.all;

  // Conteos seguros
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
          <h2 className="comments-title">Comentarios de la Audiencia Desglosados por Big Five</h2>
          <p className="comments-subtitle">
            Cada comentario público ha sido analizado e interpretado en una de las 5 dimensiones psicológicas
            fundamentales del modelo Big Five, protegiendo la identidad con cifrado irreversible SHA-256 (LOPDP).
          </p>
        </div>

        <div className="comments-search-box">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <input
            type="text"
            placeholder="Buscar por palabra en los comentarios..."
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

      {/* Pestañas de dimensiones Big Five */}
      <div className="traits-tab-container">
        {Object.entries(TRAITS_INFO).map(([key, info]) => {
          const isActive = selectedTrait === key;
          const count = counts[key] || 0;
          return (
            <button
              key={key}
              className={`trait-tab-btn ${isActive ? 'active' : ''}`}
              onClick={() => {
                setSelectedTrait(key);
                setDisplayLimit(12);
              }}
              style={{
                '--tab-color': info.color,
                borderColor: isActive ? info.color : 'transparent'
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

      {/* Cuadrícula de comentarios filtrados */}
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
                <div className="comment-card-top">
                  <div className="author-info">
                    <span className="author-hash-badge" title="Hash criptográfico SHA-256 anónimo">
                      #{c.author_hash ? c.author_hash.substring(0, 8) : 'anonimo'}
                    </span>
                    <span className="privacy-pill">Anonimizado</span>
                  </div>

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
                </div>

                <p className="comment-text">"{c.text}"</p>

                <div className="comment-card-bottom">
                  <div className="comment-why" title="Fundamento psicolingüístico">
                    <span className="why-label">Interpretación:</span>
                    <span className="why-text">{c.explanation}</span>
                  </div>

                  <div className="comment-likes" title={`${c.likes} me gusta en TikTok`}>
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
                    </svg>
                    <span>{c.likes || 0}</span>
                  </div>
                </div>
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
