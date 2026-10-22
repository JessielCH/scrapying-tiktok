import React from 'react';

export default function CreatorProfileCard({ profile, target }) {
  if (!profile && !target) return null;

  const nickname = profile?.nickname || target?.creator || 'Creador de TikTok';
  const handle = profile?.handle || target?.creator || '@usuario';
  const bio = profile?.bio || 'Perfil público analizado en la plataforma TikTok.';
  const avatarUrl = profile?.avatar_url || '';
  const isVerified = Boolean(profile?.verified);
  const followers = profile?.followers_count;
  const likes = profile?.likes_count;

  return (
    <div className="card creator-profile-card">
      <div className="creator-card-header">
        <div className="creator-avatar-wrapper">
          {avatarUrl ? (
            <img
              src={avatarUrl}
              alt={nickname}
              className="creator-avatar-img"
              referrerPolicy="no-referrer"
              crossOrigin="anonymous"
              onError={(e) => {
                // Si TikTok bloquea por CDN hotlink, mostrar avatar estilizado
                e.currentTarget.style.display = 'none';
                e.currentTarget.nextElementSibling.style.display = 'flex';
              }}
            />
          ) : null}
          <div
            className="creator-avatar-fallback"
            style={{ display: avatarUrl ? 'none' : 'flex' }}
          >
            {nickname.charAt(0).toUpperCase()}
          </div>
          {isVerified && (
            <span className="creator-verified-badge" title="Cuenta Verificada por TikTok">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
              </svg>
            </span>
          )}
        </div>

        <div className="creator-meta-info">
          <div className="creator-name-row">
            <h2 className="creator-display-name">{nickname}</h2>
            {isVerified && <span className="verified-pill">Verificado</span>}
          </div>
          <a
            href={target?.url || `https://www.tiktok.com/${handle}`}
            target="_blank"
            rel="noopener noreferrer"
            className="creator-handle-link"
          >
            {handle.startsWith('@') ? handle : `@${handle}`}
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6M15 3h6v6M10 14L21 3" />
            </svg>
          </a>

          {(followers || likes) && (
            <div className="creator-metrics-row">
              {followers && (
                <div className="creator-metric-badge">
                  <span className="metric-label">Seguidores</span>
                  <span className="metric-value">{followers}</span>
                </div>
              )}
              {likes && (
                <div className="creator-metric-badge">
                  <span className="metric-label">Me Gusta</span>
                  <span className="metric-value">{likes}</span>
                </div>
              )}
              <div className="creator-metric-badge neutral">
                <span className="metric-label">Estado</span>
                <span className="metric-value">Auditado en Vivo</span>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="creator-bio-section">
        <span className="bio-title">Biografía del Perfil:</span>
        <p className="creator-bio-text">{bio}</p>
      </div>

      <div className="creator-card-footer">
        <div className="footer-tag">
          <span className="pulse-indicator"></span>
          <span>Objetivo de Extracción: {target?.url || 'Enlace directo de TikTok'}</span>
        </div>
        <div className="footer-cert">
          <span>LOPDP Ecuador Arts. 19 & 21 • Firma SHA-256</span>
        </div>
      </div>
    </div>
  );
}
