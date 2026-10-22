import React from 'react';
import { ShieldCheck, Lock, Activity } from 'lucide-react';

export default function Header({ backendStatus }) {
  const isOnline = backendStatus?.status === 'OPERATIONAL';

  return (
    <header className="clinical-header">
      <div className="brand-badge">
        <div className="brand-icon">
          <ShieldCheck size={24} />
        </div>
        <div>
          <h1 className="brand-title">Auditoría Demográfica y Psicometría</h1>
          <p className="brand-subtitle">Plataforma de Estimación Etaria, Calidad de Audiencia y Brand Safety</p>
        </div>
      </div>

      <div className="header-meta">
        <div className="status-pill">
          <span className="status-indicator status-online"></span>
          <span>{isOnline ? 'Servidor Conectado' : 'Modo Demostración'}</span>
        </div>

        <div className="status-pill" title="Cumplimiento con LOPDP (Ecuador) Arts. 19 y 21">
          <Lock size={14} color="#64748b" />
          <span>LOPDP • SHA-256</span>
        </div>
      </div>
    </header>
  );
}
