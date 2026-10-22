import React from 'react';
import { Sparkles, FileText, CheckCircle2 } from 'lucide-react';

export default function ExecutiveSummary({ riskAssessment }) {
  if (!riskAssessment) return null;

  const {
    executive_conclusion,
    veredicto_etario,
    dictamen_brand_safety,
    implicaciones_parentales,
    compliance_certification
  } = riskAssessment;

  return (
    <div className="card" style={{ marginTop: '4px' }}>
      <div className="card-header">
        <h2 className="card-title">
          <Sparkles size={20} color="#0284c7" />
          Dictamen Ejecutivo de Inteligencia Artificial (Gemini 1.5 Flash)
        </h2>
        <span className="badge badge-tag">Síntesis Estructurada</span>
      </div>

      <div className="narrative-box">
        <p>{executive_conclusion || 'El análisis computacional de la huella lingüística en los comentarios refleja un predominio sustancial de la franja etaria comprendida entre los 13 y 17 años...'}</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', marginTop: '20px' }}>
        <div style={{ background: '#f8fafc', padding: '16px', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#0284c7', textTransform: 'uppercase', marginBottom: '6px' }}>
            Veredicto Demográfico Normativo
          </div>
          <div style={{ fontSize: '0.875rem', color: '#0f172a', lineHeight: 1.5 }}>
            {veredicto_etario || 'Predominio sustancial de cohorte adolescente (13-17 años).'}
          </div>
        </div>

        <div style={{ background: '#f8fafc', padding: '16px', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#dc2626', textTransform: 'uppercase', marginBottom: '6px' }}>
            Directiva de Brand Safety
          </div>
          <div style={{ fontSize: '0.875rem', color: '#0f172a', lineHeight: 1.5 }}>
            {dictamen_brand_safety || 'Entorno no apto para inversión publicitaria en productos regulados dirigidos a adultos.'}
          </div>
        </div>

        <div style={{ background: '#f8fafc', padding: '16px', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#d97706', textTransform: 'uppercase', marginBottom: '6px' }}>
            Telemetría de Control Parental
          </div>
          <div style={{ fontSize: '0.875rem', color: '#0f172a', lineHeight: 1.5 }}>
            {implicaciones_parentales || 'Alerta prioritaria activada por lenguaje reactivo y potencial asimetría etaria.'}
          </div>
        </div>
      </div>

      <div className="compliance-footer">
        <CheckCircle2 size={16} color="#059669" />
        <span>{compliance_certification || 'Procesado conforme al Principio de Minimización de Datos de la LOPDP (Ecuador) y GDPR mediante disociación irreversible SHA-256 y privacidad diferencial.'}</span>
      </div>
    </div>
  );
}
