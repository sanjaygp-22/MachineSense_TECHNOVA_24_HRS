import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import SidebarNavigation from '../components/layout/SidebarNavigation';
import BottomNavigation from '../components/layout/BottomNavigation';
import { API_URL } from '../config';

export default function History() {
  const [selectedMachine, setSelectedMachine] = useState('All');
  const [historyData, setHistoryData] = useState({ records: [], summary: null });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const navigate = useNavigate();

  const machines = ['All', 'id_00', 'id_02', 'id_04', 'id_06'];

  useEffect(() => {
    let isMounted = true;
    const fetchHistory = async () => {
      setLoading(true);
      setError(null);
      try {
        const url = selectedMachine === 'All'
          ? `${API_URL}/api/history?limit=100`
          : `${API_URL}/api/history/${selectedMachine}?limit=100`;

        const res = await fetch(url);
        if (!res.ok) {
          throw new Error(`Failed to fetch history (${res.status})`);
        }
        const data = await res.json();
        if (!isMounted) return;

        setHistoryData({
          records: data.records || [],
          summary: data.summary || null
        });
      } catch (err) {
        if (!isMounted) return;
        console.error("History fetch error:", err);
        setError(err.message || "Unable to load analysis history from SQLite database.");
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchHistory();
    return () => { isMounted = false; };
  }, [selectedMachine]);

  const filteredRecords = historyData.records.filter((rec) => {
    const query = search.toLowerCase();
    return (
      !search ||
      (rec.analysis_id && rec.analysis_id.toLowerCase().includes(query)) ||
      (rec.machine_id && rec.machine_id.toLowerCase().includes(query)) ||
      (rec.prediction_label && rec.prediction_label.toLowerCase().includes(query))
    );
  });

  return (
    <div className="antialiased min-h-screen flex flex-col md:flex-row bg-background text-on-background selection:bg-primary-container selection:text-on-primary-container">
      {/* Desktop Sidebar Navigation */}
      <SidebarNavigation />

      {/* Mobile Top Header */}
      <header className="md:hidden flex justify-between items-center w-full px-margin-mobile h-16 bg-surface border-b border-outline-variant sticky top-0 z-40">
        <button onClick={() => navigate('/dashboard')} className="text-primary-fixed-dim p-1">
          <span className="material-symbols-outlined">menu</span>
        </button>
        <div className="font-headline-md text-headline-md font-bold text-primary-fixed-dim tracking-tight">MachineSense</div>
        <button onClick={() => navigate('/analyze')} className="text-primary-fixed-dim p-1">
          <span className="material-symbols-outlined">sensors</span>
        </button>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 p-margin-mobile md:p-margin-desktop overflow-y-auto w-full max-w-[1600px] mx-auto pb-24 md:pb-margin-desktop">
        <header className="mb-panel-gap flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h2 className="font-headline-lg text-headline-lg text-on-surface font-bold mb-1">Analysis History</h2>
            <p className="font-body-md text-body-md text-on-surface-variant">Review past acoustic analyses and anomaly detections across all monitored assets.</p>
          </div>

          {/* Controls / Filters */}
          <div className="flex flex-wrap gap-3 items-center">
            <div className="relative w-full md:w-auto">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none text-[18px]">search</span>
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full md:w-64 bg-surface-container-low tech-border rounded py-2 pl-10 pr-4 text-on-surface font-body-sm focus:outline-none focus:border-primary-container focus:soft-cyan-glow transition-all placeholder:text-outline"
                placeholder="Search ID or Machine..."
                type="text"
              />
            </div>
            <div className="flex gap-2 w-full md:w-auto">
              <select
                value={selectedMachine}
                onChange={(e) => setSelectedMachine(e.target.value)}
                className="bg-surface-container-low tech-border rounded px-4 py-2 text-on-surface font-body-sm focus:outline-none cursor-pointer"
              >
                {machines.map((m) => (
                  <option key={m} value={m}>{m === 'All' ? 'All Machines' : m}</option>
                ))}
              </select>
              <button
                onClick={() => window.print()}
                className="flex items-center justify-center bg-primary-container text-on-primary-container font-label-caps text-label-caps px-4 py-2 rounded soft-cyan-glow transition-all font-bold cursor-pointer"
              >
                EXPORT
              </button>
            </div>
          </div>
        </header>

        {/* Data Container (Table/List View) */}
        <div className="bg-surface-container tech-border rounded-lg overflow-hidden flex flex-col">
          {/* Desktop Table Header */}
          <div className="hidden md:grid grid-cols-12 gap-4 p-4 border-b border-outline-variant bg-surface-container-low font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider items-center font-bold">
            <div className="col-span-2">Analysis ID</div>
            <div className="col-span-2">Machine</div>
            <div className="col-span-3">Date & Time</div>
            <div className="col-span-2 text-center">Prediction</div>
            <div className="col-span-1 text-right">Score</div>
            <div className="col-span-2 text-right">Peak Freq.</div>
          </div>

          {/* List Items */}
          {loading && (
            <div className="p-8 text-center text-primary-fixed-dim font-data-sm animate-pulse">
              Querying SQLite Database Records...
            </div>
          )}

          {error && (
            <div className="p-6 text-center text-error font-body-md font-semibold">
              {error}
            </div>
          )}

          {!loading && !error && filteredRecords.length === 0 && (
            <div className="p-8 text-center text-on-surface-variant font-body-md">
              No matching acoustic analysis records found in SQLite database.
            </div>
          )}

          {!loading && !error && (
            <div className="flex flex-col divide-y divide-outline-variant/40">
              {filteredRecords.map((rec) => {
                const label = (rec.prediction_label || 'NORMAL').toUpperCase();
                const isNoMachine = label === 'NO_MACHINE_SOUND';
                const isAbnormal = label === 'ABNORMAL' || label === 'CRITICAL';
                const isDegrading = label === 'DEGRADING' || label === 'WARNING';

                return (
                  <div
                    key={rec.analysis_id}
                    onClick={() => navigate(`/results?machine=${rec.machine_id}`)}
                    className="group flex flex-col md:grid md:grid-cols-12 gap-3 md:gap-4 p-4 md:items-center hover:bg-surface-container-high transition-colors cursor-pointer relative overflow-hidden"
                  >
                    <div className="col-span-2 flex justify-between items-center md:block">
                      <span className="font-data-sm text-data-sm text-on-surface font-bold">{rec.analysis_id}</span>
                      <div className="md:hidden flex items-center gap-1 px-2 py-0.5 rounded font-label-caps text-label-caps">
                        <span className={`w-1.5 h-1.5 rounded-full ${isNoMachine ? 'bg-outline' : isAbnormal ? 'bg-error' : isDegrading ? 'bg-tertiary-fixed-dim' : 'bg-secondary'}`}></span>
                        <span className={isNoMachine ? 'text-on-surface-variant' : isAbnormal ? 'text-error' : isDegrading ? 'text-tertiary-fixed-dim' : 'text-secondary'}>{label}</span>
                      </div>
                    </div>

                    <div className="col-span-2 flex flex-col gap-1">
                      <span className="font-body-sm text-body-sm text-on-surface flex items-center gap-1.5 font-semibold">
                        <span className="material-symbols-outlined text-[16px] text-on-surface-variant">settings_input_component</span>
                        {rec.machine_id}
                      </span>
                      <span className={`text-[10px] font-data-sm uppercase px-1.5 py-0.5 rounded w-fit font-bold border ${rec.source === 'rec' ? 'bg-primary-container/20 text-on-primary-container border-primary-container/30' : 'bg-surface-container-high text-on-surface-variant border-outline-variant'}`}>
                        {rec.source === 'rec' ? 'rec' : 'uploaded'}
                      </span>
                    </div>

                    <div className="col-span-3">
                      <span className="font-body-sm text-body-sm text-on-surface-variant">
                        {rec.created_at ? new Date(rec.created_at).toISOString().substring(0, 19).replace('T', ' ') + ' UTC' : '2023-10-27 14:32:05 UTC'}
                      </span>
                    </div>

                    <div className="col-span-2 hidden md:flex justify-center">
                      <div className={`flex items-center gap-1.5 border px-2.5 py-1 rounded font-label-caps text-label-caps font-bold w-fit ${
                        isNoMachine
                          ? 'bg-surface-container-high border-outline-variant text-on-surface-variant'
                          : isAbnormal
                          ? 'bg-error-container/20 border-error/40 text-error animate-pulse'
                          : isDegrading
                          ? 'bg-tertiary-container/20 border-tertiary-fixed-dim/40 text-tertiary-fixed-dim'
                          : 'bg-secondary-container/20 border-secondary/30 text-secondary'
                      }`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${isNoMachine ? 'bg-outline' : isAbnormal ? 'bg-error' : isDegrading ? 'bg-tertiary-fixed-dim' : 'bg-secondary'}`}></span>
                        {label}
                      </div>
                    </div>

                    <div className="col-span-3 flex justify-between md:contents">
                      <div className="col-span-1 md:text-right flex items-center md:block">
                        <span className="md:hidden font-label-caps text-label-caps text-on-surface-variant mr-2">SCORE</span>
                        <span className={`font-data-lg text-data-lg font-bold ${isAbnormal ? 'text-error' : isDegrading ? 'text-tertiary-fixed-dim' : 'text-on-surface'}`}>
                          {rec.rms || (isAbnormal ? '0.94' : '0.12')}
                        </span>
                      </div>
                      <div className="col-span-2 md:text-right flex items-center md:block">
                        <span className="md:hidden font-label-caps text-label-caps text-on-surface-variant mr-2">PEAK FREQ</span>
                        <span className="font-data-sm text-data-sm text-on-surface font-bold">
                          {rec.dominant_frequency_hz || '1450'} <span className="text-on-surface-variant">Hz</span>
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Pagination Footer */}
          <div className="p-4 border-t border-outline-variant bg-surface-container-low flex justify-between items-center text-on-surface-variant font-body-sm">
            <span className="font-data-sm text-data-sm">Showing 1-{filteredRecords.length} of {filteredRecords.length}</span>
            <div className="flex gap-2">
              <button className="w-8 h-8 flex items-center justify-center rounded hover:bg-surface-variant transition-colors disabled:opacity-50" disabled>
                <span className="material-symbols-outlined text-[20px]">chevron_left</span>
              </button>
              <button className="w-8 h-8 flex items-center justify-center rounded hover:bg-surface-variant transition-colors text-on-surface font-bold">
                <span className="material-symbols-outlined text-[20px]">chevron_right</span>
              </button>
            </div>
          </div>
        </div>
      </main>

      <BottomNavigation />
    </div>
  );
}
