import React, { useState } from 'react';
import { Search, Loader2 } from 'lucide-react';

export default function AuditSearch({ onAudit, isLoading }) {
  const [url, setUrl] = useState('https://www.tiktok.com/@arigameplays');
  const [sampleSize, setSampleSize] = useState(150);
  const [headed, setHeaded] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (url.trim()) {
      onAudit(url.trim(), sampleSize, headed);
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

        <select
          className="sample-select"
          value={sampleSize}
          onChange={(e) => setSampleSize(Number(e.target.value))}
          disabled={isLoading}
        >
          <option value={100}>Muestra: 100 comentarios</option>
          <option value={150}>Muestra: 150 comentarios (Recomendado)</option>
          <option value={300}>Muestra: 300 comentarios</option>
          <option value={500}>Muestra: 500 comentarios (Profundo)</option>
        </select>

        <label className="headed-toggle-label" title="Abre una ventana de navegador en pantalla por si TikTok solicita resolver un puzzle Captcha manualmente">
          <input
            type="checkbox"
            checked={headed}
            onChange={(e) => setHeaded(e.target.checked)}
            disabled={isLoading}
          />
          <span className="headed-toggle-text">🖥️ Navegador interactivo</span>
        </label>

        <button type="submit" className="btn-audit" disabled={isLoading}>
          {isLoading ? (
            <>
              <Loader2 size={18} className="animate-spin" />
              <span>Auditando en Vivo...</span>
            </>
          ) : (
            <span>Iniciar Auditoría Forense</span>
          )}
        </button>
      </form>

      <div className="quick-suggestions-row">
        <span className="quick-label">Objetivos Rápidos de Prueba:</span>
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
    </div>
  );
}
