import React from 'react';
import { AlertTriangle, ShieldCheck, ShieldAlert, AlertCircle } from 'lucide-react';

export default function RiskGauge({ riskAssessment }) {
  const defaultRisk = {
    risk_score: 74,
    risk_level: 'CRITICO',
    brand_safety_eligible: false,
    parental_alert_triggered: true
  };

  const risk = riskAssessment || defaultRisk;
  const score = risk.risk_score;

  let color = '#059669'; // Verde
  let label = 'Riesgo Bajo (Apto)';
  let badgeClass = 'badge-low';

  if (score >= 70) {
    color = '#dc2626'; // Rojo
    label = 'Riesgo Crítico';
    badgeClass = 'badge-high';
  } else if (score >= 35) {
    color = '#d97706'; // Amarillo
    label = 'Riesgo Moderado';
    badgeClass = 'badge-medium';
  }

  // Aguja del semicírculo de 0 a 180 grados
  const angle = (score / 100) * 180 - 90;

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">
          <AlertTriangle size={20} color={color} />
          Índice de Riesgo (Risk Score)
        </h2>
        <span className={`badge ${badgeClass}`}>{risk.risk_level || 'CRITICO'}</span>
      </div>

      <div className="gauge-container">
        <div className="gauge-svg-wrapper">
          <svg width="220" height="120" viewBox="0 0 220 120">
            {/* Arco de fondo */}
            <path
              d="M 20 110 A 90 90 0 0 1 200 110"
              fill="none"
              stroke="#e2e8f0"
              strokeWidth="16"
              strokeLinecap="round"
            />
            {/* Arco de color dinámico */}
            <path
              d="M 20 110 A 90 90 0 0 1 200 110"
              fill="none"
              stroke={color}
              strokeWidth="16"
              strokeLinecap="round"
              strokeDasharray="283"
              strokeDashoffset={283 - (score / 100) * 283}
              style={{ transition: 'stroke-dashoffset 0.8s ease' }}
            />
            {/* Centro de la aguja */}
            <circle cx="110" cy="110" r="8" fill="#0f172a" />
            <line
              x1="110"
              y1="110"
              x2="110"
              y2="40"
              stroke="#0f172a"
              strokeWidth="3"
              strokeLinecap="round"
              transform={`rotate(${angle} 110 110)`}
              style={{ transition: 'transform 0.8s ease' }}
            />
          </svg>
        </div>

        <div className="gauge-score" style={{ color }}>{score}</div>
        <div className="gauge-label" style={{ color }}>{label}</div>

        <div className="risk-meta-grid">
          <div className="risk-meta-box">
            <div className="risk-meta-title">Brand Safety (Marcas)</div>
            <div className="risk-meta-status" style={{ color: risk.brand_safety_eligible ? '#059669' : '#dc2626' }}>
              {risk.brand_safety_eligible ? 'Apto para Inversión' : 'Inadecuado (Menores)'}
            </div>
          </div>

          <div className="risk-meta-box">
            <div className="risk-meta-title">Control Parental (Bark Style)</div>
            <div className="risk-meta-status" style={{ color: risk.parental_alert_triggered ? '#dc2626' : '#059669' }}>
              {risk.parental_alert_triggered ? 'Alerta Activada' : 'Sin Alertas Críticas'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
