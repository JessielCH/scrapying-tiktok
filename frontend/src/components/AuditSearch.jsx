import React, { useState } from 'react';
import { Search, Loader2 } from 'lucide-react';

export default function AuditSearch({ onAudit, isLoading }) {
  const [url, setUrl] = useState('https://www.tiktok.com/@alexarmando15/video/7391823912');
  const [sampleSize, setSampleSize] = useState(150);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (url.trim()) {
      onAudit(url.trim(), sampleSize);
    }
  };

  return (
    <div className="search-card">
      <form className="search-form" onSubmit={handleSubmit}>
        <div className="search-input-wrapper">
          <Search size={18} className="search-icon" />
          <input
            type="text"
            className="clinical-input"
            placeholder="Ingresa la URL del video o perfil de TikTok a auditar (ej. https://www.tiktok.com/@creador/video/...)"
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

        <button type="submit" className="btn-audit" disabled={isLoading}>
          {isLoading ? (
            <>
              <Loader2 size={18} className="animate-spin" />
              <span>Procesando NLP...</span>
            </>
          ) : (
            <span>Auditar Objetivo</span>
          )}
        </button>
      </form>
    </div>
  );
}
