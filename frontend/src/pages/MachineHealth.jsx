import React from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import TopNavigation from '../components/layout/TopNavigation';
import BottomNavigation from '../components/layout/BottomNavigation';
import { machinesData, historyLogs } from '../data/mockData';

export default function MachineHealth() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const machineId = searchParams.get('id') || 'id_00';

  const machine = machinesData.find((m) => m.id === machineId) || machinesData[0];
  const isHealthy = machine.status === 'Healthy' || machine.status === 'Normal';

  return (
    <div className="bg-background text-on-surface min-h-screen font-body-md overflow-x-hidden pt-16 pb-24 md:pb-8 selection:bg-primary-container selection:text-on-primary-container transition-colors duration-200">
      <TopNavigation />

      <main className="max-w-7xl mx-auto px-margin-mobile md:px-margin-desktop py-panel-gap flex flex-col gap-panel-gap w-full">
        {/* Back Navigation */}
        <button
          onClick={() => navigate('/machines')}
          className="flex items-center gap-2 text-on-surface hover:text-secondary transition-colors font-label-caps text-label-caps cursor-pointer w-fit font-bold"
        >
          <span className="material-symbols-outlined text-[16px]">arrow_back</span>
          BACK TO MACHINE INVENTORY
        </button>

        {/* Header Section */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-outline-variant pb-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="font-data-sm text-data-sm text-on-surface font-bold">{machine.id}</span>
              <span className="font-data-sm text-data-sm text-on-surface-variant uppercase font-semibold">{machine.code}</span>
              <span
                className={`px-2.5 py-0.5 rounded text-xs font-data-sm uppercase font-bold flex items-center gap-1.5 border ${
                  isHealthy
                    ? 'bg-secondary-container/20 border-secondary/30 text-secondary'
                    : 'bg-tertiary-container/20 border-tertiary/40 text-tertiary'
                }`}
              >
                <span className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-secondary' : 'bg-tertiary'}`}></span>
                {machine.status}
              </span>
            </div>
            <h1 className="font-headline-lg text-headline-lg text-on-surface font-bold">
              {machine.name} <span className="text-on-surface-variant font-normal text-headline-md">• {machine.type}</span>
            </h1>
            <p className="font-body-md text-body-md text-on-surface-variant mt-1">
              Location: <strong>{machine.location}</strong> • Sector: <strong>{machine.sector || 'Main Deck'}</strong>
            </p>
          </div>

          <button
            onClick={() => navigate(`/analyze?machine=${machine.id}`)}
            className="bg-primary-container text-on-primary-container font-body-md text-body-md font-bold px-6 py-3.5 rounded soft-cyan-glow hover:bg-primary-fixed transition-all flex items-center justify-center gap-2 cursor-pointer"
          >
            <span className="material-symbols-outlined icon-fill">mic</span>
            Analyze Machine Acoustics
          </button>
        </div>

        {/* Bento Grid Layout */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-panel-gap">
          {/* Health Score Card */}
          <div className="md:col-span-4 tech-border bg-surface-container rounded-lg p-6 flex flex-col justify-between h-[220px]">
            <div className="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-widest flex items-center justify-between font-bold">
              <span>ACOUSTIC HEALTH RATING</span>
              <span className="material-symbols-outlined text-[18px]">monitor_heart</span>
            </div>
            <div className="my-2 flex items-baseline gap-2">
              <span className={`font-headline-lg text-4xl font-bold ${isHealthy ? 'text-secondary' : 'text-tertiary'}`}>
                {machine.healthScore}
              </span>
              <span className="font-data-lg text-data-lg text-on-surface-variant">%</span>
            </div>
            <div className="w-full bg-surface-container-high h-2 rounded-full overflow-hidden border border-outline-variant/30">
              <div
                className={`h-full rounded-full ${isHealthy ? 'bg-secondary' : 'bg-tertiary'}`}
                style={{ width: `${machine.healthScore}%` }}
              ></div>
            </div>
            <div className="mt-2 text-right font-data-sm text-data-sm text-on-surface-variant text-[11px] font-bold">
              LAST SCAN: {machine.lastAnalyzed.toUpperCase()}
            </div>
          </div>

          {/* Key Stats Overview */}
          <div className="md:col-span-8 tech-border bg-surface-container rounded-lg p-6 grid grid-cols-1 sm:grid-cols-3 gap-6 divide-y sm:divide-y-0 sm:divide-x divide-outline-variant/40">
            <div className="flex flex-col justify-center">
              <span className="font-label-caps text-label-caps text-on-surface-variant uppercase mb-2 font-bold">Total Analyses</span>
              <span className="font-headline-lg text-headline-lg text-on-surface font-bold">{machine.totalAnalyses || 1248}</span>
              <span className="text-secondary font-data-sm text-data-sm flex items-center gap-1 mt-1 text-xs font-bold">
                <span className="material-symbols-outlined text-[14px]">trending_up</span> +12 scans this week
              </span>
            </div>
            <div className="flex flex-col justify-center pt-4 sm:pt-0 sm:pl-6">
              <span className="font-label-caps text-label-caps text-on-surface-variant uppercase mb-2 font-bold">30D Avg Stability</span>
              <span className="font-headline-lg text-headline-lg text-on-surface font-bold">{machine.avgHealth || '94.2%'}</span>
              <span className="text-on-surface-variant font-data-sm text-data-sm mt-1 text-xs font-semibold">Baseline Stable</span>
            </div>
            <div className="flex flex-col justify-center pt-4 sm:pt-0 sm:pl-6">
              <span className="font-label-caps text-label-caps text-on-surface-variant uppercase mb-2 font-bold">Anomalies Detected</span>
              <span className="font-headline-lg text-headline-lg text-tertiary font-bold">{machine.anomalies || 0}</span>
              <span className="text-tertiary font-data-sm text-data-sm flex items-center gap-1 mt-1 text-xs font-bold">
                <span className="material-symbols-outlined text-[14px]">warning</span> Routine Inspection
              </span>
            </div>
          </div>

          {/* Health Trend Graph */}
          <div className="md:col-span-12 tech-border bg-surface-container rounded-lg p-6 flex flex-col gap-4">
            <div className="flex justify-between items-center border-b border-outline-variant pb-3">
              <span className="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider font-bold">
                Acoustic Stability Trend (30 Days)
              </span>
              <div className="flex gap-2">
                <button className="px-3 py-1 bg-surface-container-high rounded font-label-caps text-[10px] text-on-surface-variant hover:text-on-surface cursor-pointer font-bold">
                  7D
                </button>
                <button className="px-3 py-1 bg-primary-container text-on-primary-container font-label-caps text-[10px] font-bold rounded cursor-pointer">
                  30D
                </button>
                <button className="px-3 py-1 bg-surface-container-high rounded font-label-caps text-[10px] text-on-surface-variant hover:text-on-surface cursor-pointer font-bold">
                  90D
                </button>
              </div>
            </div>

            <div className="w-full h-56 relative rounded border border-outline-variant/40 overflow-hidden flex items-end bg-surface-container-low technical-grid">
              <svg className="w-full h-full absolute inset-0" preserveAspectRatio="none" viewBox="0 0 1000 200">
                <defs>
                  <linearGradient id="chartGradient" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="0%" stopColor="rgba(0, 229, 255, 0.25)"></stop>
                    <stop offset="100%" stopColor="rgba(0, 229, 255, 0)"></stop>
                  </linearGradient>
                </defs>
                <path d="M0,150 L100,140 L200,160 L300,120 L400,130 L500,80 L600,90 L700,50 L800,70 L900,40 L1000,20 L1000,200 L0,200 Z" fill="url(#chartGradient)"></path>
                <path className="drop-shadow-[0_0_8px_rgba(0,229,255,0.5)]" d="M0,150 L100,140 L200,160 L300,120 L400,130 L500,80 L600,90 L700,50 L800,70 L900,40 L1000,20" fill="none" stroke="#00e5ff" strokeWidth="2"></path>
                <circle cx="500" cy="80" fill="var(--surface)" r="4" stroke="#00e5ff" strokeWidth="2"></circle>
                <circle cx="700" cy="50" fill="var(--surface)" r="4" stroke="var(--warning)" strokeWidth="2"></circle>
                <circle cx="1000" cy="20" fill="#00e5ff" r="6"></circle>
              </svg>
              <div className="absolute left-2 top-2 bottom-6 flex flex-col justify-between font-data-sm text-data-sm text-[10px] text-on-surface-variant pointer-events-none font-bold">
                <span>100%</span>
                <span>75%</span>
                <span>50%</span>
              </div>
            </div>
          </div>

          {/* Diagnostic Log History */}
          <div className="md:col-span-12 tech-border bg-surface-container rounded-lg overflow-hidden">
            <div className="p-4 border-b border-outline-variant flex justify-between items-center bg-surface-container-low">
              <h2 className="font-label-caps text-label-caps text-on-surface-variant uppercase font-bold">
                Recent Diagnostic Logs
              </h2>
              <button
                onClick={() => navigate('/history')}
                className="text-on-surface font-label-caps text-label-caps flex items-center gap-1 hover:text-secondary cursor-pointer font-bold"
              >
                View Full SQLite History
                <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
              </button>
            </div>

            <div className="divide-y divide-outline-variant/40">
              {historyLogs.map((log) => (
                <div
                  key={log.id}
                  onClick={() => navigate(`/results?machine=${machine.id}`)}
                  className="p-4 hover:bg-surface-container-high/50 transition-colors cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                >
                  <div className="flex items-center gap-4">
                    <div
                      className={`w-9 h-9 rounded flex items-center justify-center border ${
                        log.status === 'Healthy'
                          ? 'bg-secondary-container/20 border-secondary/30 text-secondary'
                          : 'bg-tertiary-container/20 border-tertiary/40 text-tertiary'
                      }`}
                    >
                      <span className="material-symbols-outlined text-[18px]">
                        {log.status === 'Healthy' ? 'check_circle' : 'warning'}
                      </span>
                    </div>
                    <div>
                      <div className="font-body-md text-body-md font-semibold text-on-surface">{log.type}</div>
                      <div className="font-data-sm text-data-sm text-on-surface-variant text-[11px] mt-0.5 font-medium">{log.time}</div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between sm:justify-end gap-6 sm:w-1/2 font-data-sm text-data-sm">
                    <div className="flex flex-col">
                      <span className="text-on-surface-variant text-[10px] uppercase font-bold">STATUS</span>
                      <span className={`font-bold ${log.status === 'Healthy' ? 'text-secondary' : 'text-tertiary'}`}>
                        {log.status.toUpperCase()}
                      </span>
                    </div>
                    <div className="hidden sm:flex flex-col">
                      <span className="text-on-surface-variant text-[10px] uppercase font-bold">DURATION</span>
                      <span className="text-on-surface font-semibold">{log.duration}</span>
                    </div>
                    <button className="px-3 py-1 bg-surface-container-high border border-outline-variant text-on-surface font-label-caps text-label-caps rounded hover:bg-surface-variant transition-colors cursor-pointer font-bold">
                      Inspect →
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>

      <BottomNavigation />
    </div>
  );
}
