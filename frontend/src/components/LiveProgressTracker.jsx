import React, { useState, useEffect, useRef } from 'react';
import { Activity, Terminal, CheckCircle2, Clock } from 'lucide-react';

export default function LiveProgressTracker({ isRunning }) {
  const [progressData, setProgressData] = useState({
    phase: 'INIT',
    percent: 10,
    message: 'Conectando con TikTok e inicializando sesión...',
    logs: ['[00:00:01] Iniciando extracción de datos...'],
    is_running: true
  });
  const logsEndRef = useRef(null);

  useEffect(() => {
    if (!isRunning) return;

    const interval = setInterval(async () => {
      try {
        const res = await fetch('/api/v1/audit/progress');
        if (res.ok) {
          const data = await res.json();
          setProgressData(data);
        }
      } catch (e) {
        // Fallback progress tick si la red está ocupada
        setProgressData(prev => ({
          ...prev,
          percent: Math.min(95, prev.percent + 2),
          message: 'Procesando publicaciones y psicometría lingüística...'
        }));
      }
    }, 700);

    return () => clearInterval(interval);
  }, [isRunning]);

  useEffect(() => {
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [progressData.logs]);

  return (
    <div className="live-progress-card">
      <div className="progress-header">
        <div className="progress-title-wrap">
          <span className="pulse-beacon"></span>
          <Activity size={18} className="progress-icon text-cyan" />
          <h4 className="progress-title">Progreso de Extracción en Tiempo Real</h4>
        </div>
        <span className="progress-percentage-pill">{progressData.percent}%</span>
      </div>

      {/* Barra de progreso animada */}
      <div className="progress-bar-track">
        <div
          className="progress-bar-fill"
          style={{ width: `${progressData.percent}%` }}
        >
          <div className="progress-shimmer"></div>
        </div>
      </div>

      <p className="progress-current-message">
        <Clock size={14} className="inline mr-1" />
        {progressData.message}
      </p>

      {/* Terminal de registros en vivo */}
      <div className="live-terminal-box">
        <div className="terminal-topbar">
          <Terminal size={13} />
          <span>Consola de Extracción en Vivo</span>
        </div>
        <div className="terminal-logs-scroll">
          {progressData.logs.map((log, i) => (
            <div key={i} className="terminal-log-row">
              <CheckCircle2 size={12} className="log-check text-cyan" />
              <span className="log-text">{log}</span>
            </div>
          ))}
          <div ref={logsEndRef} />
        </div>
      </div>
    </div>
  );
}
