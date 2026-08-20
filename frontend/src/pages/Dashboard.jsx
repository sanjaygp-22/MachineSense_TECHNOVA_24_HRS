import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import TopNavigation from '../components/layout/TopNavigation';
import BottomNavigation from '../components/layout/BottomNavigation';
import TrendChart from '../components/charts/TrendChart';
import { machinesData as initialMachines } from '../data/mockData';
import { API_URL } from '../config';

export default function Dashboard() {
  const navigate = useNavigate();
  const [machines, setMachines] = useState(initialMachines);
  const [historyRecords, setHistoryRecords] = useState([]);

  useEffect(() => {
    let isMounted = true;
    const fetchHistory = async () => {
      try {
        const res = await fetch(`${API_URL}/api/history?limit=100`);
        if (res.ok) {
          const data = await res.json();
          const records = data.records || [];
          if (!isMounted) return;
          setHistoryRecords(records);

          if (records.length > 0) {
            // Map latest prediction status per machine_id
            const updated = initialMachines.map((m) => {
              const latestRec = records.find((r) => r.machine_id === m.id);
              if (!latestRec) return m;
              const lbl = (latestRec.prediction_label || '').toLowerCase();
              let newStatus = m.status;
              let score = m.healthScore;

              if (lbl === 'normal') {
                newStatus = 'Healthy';
                score = Math.round(100 - (latestRec.abnormal_probability * 100));
              } else if (lbl === 'abnormal') {
                newStatus = 'Critical';
                score = Math.round((1 - latestRec.abnormal_probability) * 100);
              } else if (lbl === 'no_machine_sound') {
                newStatus = 'No Machine';
                score = 0;
              }
              return { ...m, status: newStatus, healthScore: Math.max(0, Math.min(100, score)) };
            });
            setMachines(updated);
          }
        }
      } catch (err) {
        console.error("Dashboard history fetch error:", err);
      }
    };
    fetchHistory();
    return () => { isMounted = false; };
  }, []);

  const totalMachines = machines.length;
  const healthyCount = machines.filter((m) => m.status === 'Healthy' || m.status === 'Normal').length;
  const alertCount = machines.filter((m) => m.status !== 'Healthy' && m.status !== 'Normal' && m.status !== 'No Machine').length;

  return (
    <div className="min-h-screen pb-24 md:pb-8 flex flex-col font-body-md text-body-md bg-background text-on-surface selection:bg-primary-container selection:text-on-primary-container transition-colors duration-200">
      <TopNavigation />

      <main className="flex-1 px-margin-mobile md:px-margin-desktop py-panel-gap mt-16 max-w-7xl mx-auto w-full flex flex-col gap-panel-gap">
        {/* Greeting Section */}
        <section className="flex flex-col gap-2">
          <h1 className="font-headline-lg text-headline-lg text-on-surface font-bold tracking-tight">
            Good morning, <span className="text-on-surface border-b-2 border-primary-container">Engineer</span>
          </h1>
          <p className="font-body-md text-body-md text-on-surface-variant">
            Monitor machine acoustic health and investigate abnormal operating behavior in real time.
          </p>
        </section>

        {/* Top Stats Grid */}
        <section className="grid grid-cols-2 md:grid-cols-3 gap-gutter">
          {/* Overall Health Card */}
          <div className="tech-border bg-surface-container rounded-lg p-4 flex flex-col items-center justify-center gap-3 col-span-2 md:col-span-1 h-36 relative overflow-hidden">
            <div className="w-full flex justify-between items-center">
              <span className="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-widest font-bold">
                Overall Health
              </span>
              <span className="flex items-center gap-1.5 bg-secondary-container/20 border border-secondary/30 px-2 py-0.5 rounded text-[10px] font-data-sm text-secondary font-bold">
                <span className="w-1.5 h-1.5 rounded-full bg-secondary pulse-dot"></span>
                <span>OPTIMAL</span>
              </span>
            </div>
            <div className="relative w-16 h-16 radial-progress" style={{ '--value': '94%' }}>
              <span className="relative z-10 font-data-lg text-data-lg text-on-surface font-bold">
                94<span className="font-data-sm text-data-sm text-on-surface-variant">%</span>
              </span>
            </div>
          </div>

          {/* Machines Monitored */}
          <div className="tech-border bg-surface-container rounded-lg p-4 flex flex-col justify-between h-36">
            <span className="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-widest font-bold">
              Machines Monitored
            </span>
            <div className="flex items-baseline justify-between">
              <span className="font-headline-lg text-headline-lg text-on-surface font-bold">
                {totalMachines}
              </span>
              <span className="font-data-sm text-data-sm text-secondary font-bold">
                {healthyCount} Healthy
              </span>
            </div>
          </div>

          {/* Recent Alerts */}
          <div className="tech-border bg-surface-container rounded-lg p-4 flex flex-col justify-between h-36 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-16 h-16 bg-error/10 blur-xl rounded-full translate-x-1/2 -translate-y-1/2"></div>
            <span className="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-widest font-bold">
              Active Alerts
            </span>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="font-headline-lg text-headline-lg text-error font-bold">
                  {alertCount}
                </span>
                <span className="w-2.5 h-2.5 rounded-full bg-error animate-pulse"></span>
              </div>
              <button
                onClick={() => navigate('/machines')}
                className="font-label-caps text-label-caps text-on-surface hover:text-secondary cursor-pointer uppercase font-bold"
              >
                Inspect Fleet →
              </button>
            </div>
          </div>
        </section>

        {/* Acoustic Analysis CTA Banner */}
        <section className="tech-border bg-surface-container rounded-lg p-6 flex flex-col gap-4 relative overflow-hidden">
          <div className="flex items-center justify-between border-b border-outline-variant pb-3">
            <span className="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-widest flex items-center gap-2 font-bold">
              <span className="material-symbols-outlined text-[16px] text-on-surface icon-fill">hearing</span>
              Acoustic Diagnostic Pipeline
            </span>
            <span className="font-data-sm text-data-sm text-on-surface font-semibold">16 kHz Mono PCM</span>
          </div>

          <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
            <div className="flex-1">
              <h3 className="font-headline-md text-headline-md text-on-surface mb-1 font-bold">
                Analyze Machine Acoustics
              </h3>
              <p className="font-body-md text-body-md text-on-surface-variant">
                Place your recording device near the machinery or upload a WAV recording to run machine-invariant RF anomaly inference.
              </p>
            </div>

            <button
              onClick={() => navigate('/analyze')}
              className="bg-primary-container text-on-primary-container font-body-md text-body-md font-bold py-3.5 px-8 rounded soft-cyan-glow hover:bg-primary-fixed transition-all flex items-center justify-center gap-2 w-full md:w-auto cursor-pointer"
            >
              <span className="material-symbols-outlined">graphic_eq</span>
              Start Machine Diagnostic
            </button>
          </div>
        </section>

        {/* My Machines Inventory Section */}
        <section className="flex flex-col gap-4">
          <div className="flex justify-between items-center">
            <h2 className="font-headline-md text-headline-md text-on-surface font-bold">Active Machine Fleet</h2>
            <button
              onClick={() => navigate('/machines')}
              className="font-label-caps text-label-caps text-on-surface hover:text-secondary transition-colors flex items-center gap-1 cursor-pointer font-bold"
            >
              VIEW ALL MACHINES ({machines.length})
              <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-gutter">
            {machines.map((machine) => {
              const isHealthy = machine.status === 'Healthy';
              const isWarning = machine.status === 'Warning';
              return (
                <div
                  key={machine.id}
                  className="tech-border bg-surface-container rounded-lg p-5 flex flex-col justify-between gap-4 hover:border-outline transition-all group relative overflow-hidden"
                >
                  <div className="flex justify-between items-start">
                    <div className="flex flex-col">
                      <span className="font-data-sm text-data-sm text-on-surface-variant uppercase mb-0.5 font-bold">
                        {machine.id}
                      </span>
                      <h3 className="font-headline-md text-body-lg text-on-surface font-bold group-hover:text-secondary transition-colors">
                        {machine.name}
                      </h3>
                      <span className="font-body-sm text-body-sm text-on-surface-variant text-xs mt-0.5">
                        {machine.type}
                      </span>
                    </div>

                    <div
                      className={`flex items-center gap-1.5 px-2 py-1 rounded text-xs font-data-sm uppercase font-bold border ${
                        isHealthy
                          ? 'bg-secondary-container/20 border-secondary/30 text-secondary'
                          : isWarning
                          ? 'bg-tertiary-container/20 border-tertiary-container/40 text-tertiary'
                          : 'bg-error/20 border-error/40 text-error animate-pulse'
                      }`}
                    >
                      <span
                        className={`w-2 h-2 rounded-full ${
                          isHealthy ? 'bg-secondary' : isWarning ? 'bg-tertiary' : 'bg-error'
                        }`}
                      ></span>
                      {machine.status}
                    </div>
                  </div>

                  <div className="h-px bg-outline-variant/40 w-full"></div>

                  <div className="grid grid-cols-2 gap-2 font-data-sm text-data-sm">
                    <div>
                      <span className="text-on-surface-variant text-[10px] uppercase block font-bold">Location</span>
                      <span className="text-on-surface text-xs font-semibold">{machine.location}</span>
                    </div>
                    <div className="text-right">
                      <span className="text-on-surface-variant text-[10px] uppercase block font-bold">Health Score</span>
                      <span className={`text-xs font-bold ${isHealthy ? 'text-secondary' : isWarning ? 'text-tertiary' : 'text-error'}`}>
                        {machine.healthScore}%
                      </span>
                    </div>
                  </div>

                  <button
                    onClick={() => navigate(`/analyze?machine=${machine.id}`)}
                    className="w-full mt-2 bg-surface-container-high border border-outline-variant text-on-surface hover:bg-primary-container hover:text-on-primary-container font-label-caps text-label-caps py-2 rounded transition-all flex items-center justify-center gap-1 cursor-pointer font-bold"
                  >
                    Analyze Asset
                    <span className="material-symbols-outlined text-[16px]">chevron_right</span>
                  </button>
                </div>
              );
            })}
          </div>
        </section>

        {/* Fleet Health Trend Chart Panel */}
        <section className="tech-border bg-surface-container rounded-lg p-6 flex flex-col gap-4 relative overflow-hidden">
          <div className="flex justify-between items-center border-b border-outline-variant pb-3">
            <h3 className="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider flex items-center gap-2 font-bold">
              <span className="material-symbols-outlined text-[16px] text-on-surface">show_chart</span>
              Fleet Acoustic Health Trend (7 Days)
            </h3>
            <span className="font-data-sm text-data-sm text-secondary flex items-center gap-1.5 font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-secondary"></span>
              94.2% Stability Avg
            </span>
          </div>

          <TrendChart records={historyRecords} height={180} />
        </section>
      </main>

      <BottomNavigation />
    </div>
  );
}
