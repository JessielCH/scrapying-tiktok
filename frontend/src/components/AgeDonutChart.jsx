import React from 'react';
import { Users } from 'lucide-react';

export default function AgeDonutChart({ ageDistribution, sampleSize }) {
  const defaultDist = {
    '13-17': 42.5,
    '18-24': 35.0,
    '25-34': 15.5,
    '35-44': 5.0,
    '45+': 2.0
  };

  const dist = ageDistribution || defaultDist;

  // Paleta clínica sobria
  const colors = {
    '13-17': '#dc2626', // Carmesí para franja de menores
    '18-24': '#0284c7', // Azul primario
    '25-34': '#059669', // Verde esmeralda
    '35-44': '#d97706', // Ámbar
    '45+': '#64748b'    // Gris pizarra
  };

  const labels = {
    '13-17': '13 - 17 años (Menores)',
    '18-24': '18 - 24 años (Jóvenes)',
    '25-34': '25 - 34 años (Adultos)',
    '35-44': '35 - 44 años (Maduros)',
    '45+': '45+ años (Mayores)'
  };

  // Cálculo de los arcos del SVG Donut
  const entries = Object.entries(dist);
  let cumulativePercent = 0;

  const slices = entries.map(([group, percent]) => {
    const startAngle = (cumulativePercent / 100) * 360;
    cumulativePercent += percent;
    const endAngle = (cumulativePercent / 100) * 360;

    const startRad = (startAngle - 90) * (Math.PI / 180);
    const endRad = (endAngle - 90) * (Math.PI / 180);

    const x1 = 90 + 70 * Math.cos(startRad);
    const y1 = 90 + 70 * Math.sin(startRad);
    const x2 = 90 + 70 * Math.cos(endRad);
    const y2 = 90 + 70 * Math.sin(endRad);

    const largeArcFlag = percent > 50 ? 1 : 0;
    const pathData = `M 90 90 L ${x1} ${y1} A 70 70 0 ${largeArcFlag} 1 ${x2} ${y2} Z`;

    return {
      group,
      percent,
      pathData,
      color: colors[group] || '#94a3b8'
    };
  });

  const minorPercentage = dist['13-17'] || 0;

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">
          <Users size={20} color="#0284c7" />
          Distribución de Edad Real Estimada (Big Five + NLP)
        </h2>
        <span className="badge badge-tag">
          {sampleSize > 0 ? `Muestra: ${sampleSize} comentarios` : 'Sin comentarios extraídos'}
        </span>
      </div>

      <div className="donut-container">
        <div className="donut-svg-wrapper">
          <svg width="180" height="180" viewBox="0 0 180 180">
            {slices.map((slice, i) => (
              <path
                key={i}
                d={slice.pathData}
                fill={slice.color}
                stroke="#ffffff"
                strokeWidth="2"
              />
            ))}
            {/* Círculo central para transformar en gráfico de anillo (Donut) */}
            <circle cx="90" cy="90" r="48" fill="#ffffff" />
          </svg>

          <div className="donut-center-text">
            <div className="donut-center-value">{minorPercentage}%</div>
            <div className="donut-center-label">Menores (13-17)</div>
          </div>
        </div>

        <div className="donut-legend">
          {entries.map(([group, val]) => (
            <div key={group} className="legend-item">
              <div className="legend-left">
                <span
                  className="legend-color-dot"
                  style={{ backgroundColor: colors[group] }}
                ></span>
                <span>{labels[group]}</span>
              </div>
              <span className="legend-value">{val}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
