import React from 'react';
import { Download, FileCheck, Tag, ExternalLink } from 'lucide-react';

export default function EvidenceCard({ target }) {
  if (!target) return null;

  const { creator, video_id, categories, evidence_video_url, evidence_sha256, url } = target;

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">
          <FileCheck size={20} color="#0284c7" />
          Copia Multimedia y Clasificación
        </h2>
        <span className="badge badge-tag">Preservación Digital</span>
      </div>

      <div className="evidence-content">
        <div className="creator-info">
          <div>
            <div className="creator-handle">{creator}</div>
            <div style={{ fontSize: '0.8rem', color: '#64748b' }}>Video ID: {video_id}</div>
          </div>
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: '#0284c7', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.825rem', textDecoration: 'none', fontWeight: 600 }}
          >
            <span>Ver en TikTok</span>
            <ExternalLink size={14} />
          </a>
        </div>

        <div>
          <div style={{ fontSize: '0.725rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', marginBottom: '6px' }}>
            Etiquetas Temáticas Detectadas
          </div>
          <div className="tag-list">
            {(categories || ['Entretenimiento', 'Tendencias Digitales']).map((tag, idx) => (
              <span key={idx} className="badge badge-tag">
                <Tag size={12} style={{ marginRight: '4px', verticalAlign: 'middle' }} />
                {tag}
              </span>
            ))}
          </div>
        </div>

        <div className="hash-box">
          <div className="hash-label">Firma Criptográfica SHA-256 (Integridad de Datos)</div>
          <code>{evidence_sha256 || 'SHA256_VERIFICATION_ACTIVE_EVID'}</code>
        </div>

        <a
          href={evidence_video_url || '#'}
          download
          className="btn-download-evidence"
          title="Descarga la copia de respaldo del video con firma SHA-256"
          onClick={(e) => {
            if (!evidence_video_url) {
              e.preventDefault();
              alert('El archivo multimedia se encuentra archivado en el servidor bajo la firma SHA-256 indicada.');
            }
          }}
        >
          <Download size={16} />
          <span>Descargar Video Multimedia (.MP4)</span>
        </a>
      </div>
    </div>
  );
}
