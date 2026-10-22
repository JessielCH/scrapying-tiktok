import React, { useState } from 'react';
import { Search, Loader2, Film } from 'lucide-react';

export default function AuditSearch({ onAudit, isLoading }) {
  const [url, setUrl] = useState('https://www.tiktok.com/@arigameplays');
  const [sampleSize, setSampleSize] = useState(150);
  const [maxVideos, setMaxVideos] = useState(10);
  const [headed, setHeaded] = useState(true);
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [authSuccess, setAuthSuccess] = useState(false);

  const handleTriggerQR = async () => {
    setIsAuthenticating(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/session/login-qr', { method: 'POST' });
      const data = await res.json();
      if (data.is_authenticated) {
        setAuthSuccess(true);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsAuthenticating(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (url.trim()) {
      onAudit(url.trim(), sampleSize, maxVideos, headed);
    }
  };

  const QUICK_PROFILES = [
    { label: '@arigameplays', url: 'https://www.tiktok.com/@arigameplays' },
    { label: '@khaby.lame', url: 'https://www.tiktok.com/@khaby.lame' },
    { label: '@mrbeast', url: 'https://www.tiktok.com/@mrbeast' }
  ];

  return (
    <div className="search-card">
      <form className="search-form" onSubmit={handleSubmit}>
        <div className="search-input-wrapper">
          <Search size={18} className="search-icon" />
          <input
            type="text"
            className="clinical-input"
            placeholder="Pega la URL de un perfil o video de TikTok (ej. https://www.tiktok.com/@creador)"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={isLoading}
            required
          />
        </div>

        {/* Selector de publicaciones a analizar (hasta 30) */}
        <div className="select-wrapper-with-icon" title="Cantidad de publicaciones/videos recientes a extraer">
          <Film size={15} className="select-inner-icon" />
          <select
            className="sample-select video-count-select"
            value={maxVideos}
            onChange={(e) => setMaxVideos(Number(e.target.value))}
            disabled={isLoading}
          >
            <option value={5}>Extraer: 5 videos</option>
            <option value={10}>Extraer: 10 videos (Recomendado)</option>
            <option value={20}>Extraer: 20 videos</option>
            <option value={30}>Extraer: 30 videos (Completo)</option>
          </select>
        </div>

        {/* Selector de muestra de comentarios */}
        <select
          className="sample-select"
          value={sampleSize}
          onChange={(e) => setSampleSize(Number(e.target.value))}
          disabled={isLoading}
        >
          <option value={100}>Muestra: 100 comentarios</option>
          <option value={150}>Muestra: 150 comentarios</option>
          <option value={300}>Muestra: 300 comentarios</option>
          <option value={500}>Muestra: 500 comentarios (Profundo)</option>
        </select>

        {/* Casilla de navegador visible interactivo */}
        <label className="headed-toggle-label" title="Abre una ventana de navegador visible para resolver el puzle deslizador de TikTok si la plataforma lo solicita">
          <input
            type="checkbox"
            checked={headed}
            onChange={(e) => setHeaded(e.target.checked)}
            disabled={isLoading}
          />
          <span className="headed-toggle-text">🖥️ Navegador visible (Para puzzle)</span>
        </label>

        <button type="submit" className="btn-audit" disabled={isLoading}>
          {isLoading ? (
            <>
              <Loader2 size={18} className="animate-spin" />
              <span>Extrayendo en Vivo...</span>
            </>
          ) : (
            <span>Iniciar Extracción de Datos</span>
          )}
        </button>
      </form>

      <div className="quick-suggestions-row" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', flexWrap: 'wrap' }}>
          <span className="quick-label">Objetivos Rápidos:</span>
          {QUICK_PROFILES.map((p) => (
            <button
              key={p.label}
              type="button"
              className="quick-chip-btn"
              onClick={() => setUrl(p.url)}
              disabled={isLoading}
            >
              {p.label}
            </button>
          ))}
        </div>

        <button
          type="button"
          className={`btn-qr-auth ${authSuccess ? 'auth-success' : ''}`}
          onClick={handleTriggerQR}
          disabled={isLoading || isAuthenticating}
          title="Abre una ventana con código QR para vincular tu cuenta de TikTok (tiempo disponible: 5 minutos para escanear y resolver sin prisa)"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.35rem 0.8rem',
            fontSize: '0.8rem',
            fontWeight: 600,
            borderRadius: '0.5rem',
            background: authSuccess ? 'rgba(16, 185, 129, 0.15)' : 'rgba(254, 44, 85, 0.12)',
            color: authSuccess ? '#10b981' : '#fe2c55',
            border: authSuccess ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(254, 44, 85, 0.3)',
            cursor: 'pointer',
            transition: 'all 0.2s ease'
          }}
        >
          {isAuthenticating ? (
            <>
              <Loader2 size={13} className="animate-spin" />
              <span>Esperando QR (5 min)...</span>
            </>
          ) : authSuccess ? (
            <span>✅ Sesión Conectada</span>
          ) : (
            <span>🔑 Conectar Sesión TikTok (Login QR)</span>
          )}
        </button>
      </div>
    </div>
  );
}
