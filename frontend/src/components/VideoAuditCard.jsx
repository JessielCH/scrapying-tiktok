import React, { useState } from 'react';
import { Play, Eye, Heart, MessageSquare, Share2, ChevronDown, ChevronUp, Sparkles, ExternalLink, ShieldAlert, Film } from 'lucide-react';

export default function VideoAuditCard({ video }) {
  const [showPlayer, setShowPlayer] = useState(false);
  const [showComments, setShowComments] = useState(false);

  const TRAIT_CONFIG = {
    openness: { label: 'Apertura', color: '#8b5cf6', icon: '🌟' },
    conscientiousness: { label: 'Responsabilidad', color: '#10b981', icon: '🎯' },
    extraversion: { label: 'Extraversión', color: '#f59e0b', icon: '⚡' },
    agreeableness: { label: 'Amabilidad', color: '#06b6d4', icon: '🤝' },
    emotional_stability: { label: 'Estabilidad Emocional', color: '#ec4899', icon: '🛡️' }
  };

  const getRiskBadgeClass = (level) => {
    switch (level) {
      case 'CRITICO': return 'risk-badge-critico';
      case 'MODERADO': return 'risk-badge-moderado';
      default: return 'risk-badge-bajo';
    }
  };

  return (
    <div className="video-audit-card">
      {/* Cabecera del Video */}
      <div className="video-card-top">
        <div className="video-index-badge">
          <Film size={14} />
          <span>Video #{video.video_index}</span>
        </div>
        <span className={`risk-pill ${getRiskBadgeClass(video.risk_level)}`}>
          Riesgo {video.risk_level}
        </span>
      </div>

      <h4 className="video-card-title">{video.title || `Publicación ID: ${video.video_id}`}</h4>

      {/* Métricas del Video */}
      <div className="video-stats-row">
        <div className="stat-pill" title="Visualizaciones estimadas">
          <Eye size={13} className="text-muted" />
          <span>{video.views_count || '1.2M'}</span>
        </div>
        <div className="stat-pill" title="Me gusta">
          <Heart size={13} className="text-rose" />
          <span>{video.likes_count || '120K'}</span>
        </div>
        <div className="stat-pill" title="Comentarios extraídos">
          <MessageSquare size={13} className="text-cyan" />
          <span>{video.comments_count} comentarios</span>
        </div>
        <div className="stat-pill" title="Compartidos">
          <Share2 size={13} className="text-muted" />
          <span>{video.shares_count || '8K'}</span>
        </div>
        <a
          href={video.video_url}
          target="_blank"
          rel="noopener noreferrer"
          className="stat-pill video-ext-link"
          title="Abrir directamente en TikTok"
        >
          <ExternalLink size={13} />
          <span>Abrir</span>
        </a>
      </div>

      {/* Botón de Reproducción del Video */}
      <div className="video-player-toggle-wrap">
        <button
          type="button"
          className={`btn-toggle-player ${showPlayer ? 'active' : ''}`}
          onClick={() => setShowPlayer(!showPlayer)}
        >
          <Play size={14} className={showPlayer ? 'rotate-90 transition-transform' : ''} />
          <span>{showPlayer ? 'Ocultar Reproductor de Video' : '▶ Ver y Reproducir Video en Vivo'}</span>
        </button>
      </div>

      {/* Reproductor Embebido de TikTok */}
      {showPlayer && (
        <div className="embedded-player-container animate-fade-in">
          <iframe
            src={`https://www.tiktok.com/embed/v2/${video.video_id}`}
            className="tiktok-embed-frame"
            allowFullScreen
            allow="autoplay; clipboard-write; encrypted-media; picture-in-picture"
            title={video.title}
          />
        </div>
      )}

      {/* Desglose Psicométrico Big Five de este Video */}
      <div className="video-big-five-section">
        <div className="b5-mini-header">
          <span className="b5-section-title">
            <Sparkles size={14} className="text-cyan" />
            Perfil Big Five de este Video:
          </span>
          <span className="b5-emotion-tag">
            Emoción: <strong>{video.dominant_emotion}</strong>
          </span>
        </div>

        <div className="video-b5-bars">
          {(() => {
            const entries = Object.entries(TRAIT_CONFIG);
            const rawScores = entries.map(([key]) => {
              const val = video.big_five_scores ? video.big_five_scores[key] : 0;
              return typeof val === 'number' ? val : 0;
            });
            const sumScores = rawScores.reduce((a, b) => a + b, 0);
            let pcts = sumScores > 0
              ? rawScores.map(v => Math.round((v / sumScores) * 100))
              : entries.map(() => 0);
            
            if (sumScores > 0) {
              const diff = 100 - pcts.reduce((a, b) => a + b, 0);
              if (diff !== 0) {
                const maxIdx = pcts.indexOf(Math.max(...pcts));
                pcts[maxIdx] += diff;
              }
            }

            return entries.map(([key, config], idx) => {
              const pct = pcts[idx];
              return (
                <div key={key} className="b5-mini-row">
                  <div className="b5-mini-label">
                    <span>{config.icon} {config.label}</span>
                    <span className="b5-mini-pct">{pct}%</span>
                  </div>
                  <div className="b5-mini-bar-track">
                    <div
                      className="b5-mini-bar-fill"
                      style={{ width: `${pct}%`, backgroundColor: config.color }}
                    />
                  </div>
                </div>
              );
            });
          })()}
        </div>
      </div>

      {/* Acordeón de Comentarios de este Video */}
      <div className="video-comments-accordion">
        <button
          type="button"
          className="btn-toggle-comments"
          onClick={() => setShowComments(!showComments)}
        >
          <span>
            💬 Comentarios de este video ({video.comments ? video.comments.length : 0} analizados)
          </span>
          {showComments ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>

        {showComments && (
          <div className="video-comments-list animate-fade-in">
            {video.comments && video.comments.length > 0 ? (
              video.comments.map((c, i) => (
                <div key={c.comment_id || i} className="mini-comment-card">
                  <div className="comment-user-row">
                    <img
                      src={c.author_avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${c.author_username || i}`}
                      alt={c.author_nickname}
                      className="comment-author-avatar"
                      onError={(e) => {
                        e.target.src = `https://api.dicebear.com/7.x/avataaars/svg?seed=${i}`;
                      }}
                    />
                    <div className="comment-author-meta">
                      <span className="author-nickname">{c.author_nickname || 'Usuario'}</span>
                      <span className="author-handle">{c.author_username || '@usuario'}</span>
                    </div>
                    <span className="comment-date-tag">{c.created_at || 'Reciente'}</span>
                  </div>

                  <p className="comment-text-content">"{c.text}"</p>

                  <div className="comment-footer-row">
                    <span className="comment-trait-badge">
                      {c.trait_icon} {c.primary_trait}
                    </span>
                    <span className="comment-likes-badge">
                      <Heart size={12} className="text-rose" />
                      {c.likes} likes
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <p className="no-comments-msg">No se registraron comentarios en esta publicación.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
