import React from 'react';
import { Brain, Sparkles } from 'lucide-react';

export default function BigFiveProfile({ psychometrics, dominantEmotion, aqsScore }) {
  const defaultScores = {
    conscientiousness: 0.28,
    social_dominance: 0.68,
    emotional_stability: 0.35,
    agreeableness: 0.52,
    openness: 0.74
  };

  const scores = psychometrics || defaultScores;

  const traitConfigs = [
    {
      key: 'conscientiousness',
      label: 'Responsabilidad (Autocontrol y Maduración)',
      desc: 'Bajo en adolescencia, escala con roles adultos (Roberts et al., 2006)',
      value: scores.conscientiousness || 0.3,
      color: '#0284c7'
    },
    {
      key: 'social_dominance',
      label: 'Dominancia Social (Asertividad Lingüística)',
      desc: 'Picos dramáticos en la juventud y veintena',
      value: scores.social_dominance || 0.6,
      color: '#7c3aed'
    },
    {
      key: 'emotional_stability',
      label: 'Estabilidad Emocional (Inverso de Neuroticismo)',
      desc: 'Labilidad reactiva en adolescentes, estabilidad en adultez media',
      value: scores.emotional_stability || 0.35,
      color: '#059669'
    },
    {
      key: 'openness',
      label: 'Apertura a la Experiencia',
      desc: 'Alta creatividad y consumo de novedades en audiencias jóvenes',
      value: scores.openness || 0.7,
      color: '#d97706'
    },
    {
      key: 'agreeableness',
      label: 'Amabilidad Comunitaria',
      desc: 'Empatía y cohesión comunicacional con la comunidad',
      value: scores.agreeableness || 0.0,
      color: '#64748b'
    }
  ];

  // Garantizar que la suma de porcentajes sea exactamente 100% (o 0% si no hay datos)
  const sumScores = traitConfigs.reduce((acc, t) => acc + (Number(t.value) || 0), 0);
  let pcts = [];
  if (sumScores > 0) {
    pcts = traitConfigs.map(t => Math.round(((Number(t.value) || 0) / sumScores) * 100));
    const diff = 100 - pcts.reduce((a, b) => a + b, 0);
    if (diff !== 0) {
      const maxIdx = pcts.indexOf(Math.max(...pcts));
      pcts[maxIdx] += diff;
    }
  } else {
    pcts = traitConfigs.map(() => 0);
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">
          <Brain size={20} color="#0284c7" />
          Perfil Psicométrico de Audiencia (Big Five)
        </h2>
        <div style={{ display: 'flex', gap: '8px' }}>
          <span className="badge badge-tag">AQS: {aqsScore || 78}/100</span>
          <span className="badge badge-tag">Afecto: {dominantEmotion || 'Alegría'}</span>
        </div>
      </div>

      <div className="b5-list">
        {traitConfigs.map((t, idx) => {
          const percent = pcts[idx];
          return (
            <div key={t.key} className="b5-item">
              <div className="b5-header">
                <div>
                  <div>{t.label}</div>
                  <div style={{ fontSize: '0.725rem', color: '#64748b', fontWeight: 400 }}>{t.desc}</div>
                </div>
                <span style={{ color: t.color }}>{percent}%</span>
              </div>
              <div className="b5-bar-bg">
                <div
                  className="b5-bar-fill"
                  style={{ width: `${percent}%`, backgroundColor: t.color }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
