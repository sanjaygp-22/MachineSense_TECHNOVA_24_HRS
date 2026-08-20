import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import SidebarNavigation from '../components/layout/SidebarNavigation';
import BottomNavigation from '../components/layout/BottomNavigation';
import { useTheme } from '../context/ThemeContext';
import { machinesData } from '../data/mockData';

export default function Settings() {
  const navigate = useNavigate();
  const { theme, setTheme } = useTheme();

  const [targetMachine, setTargetMachine] = useState('id_00');
  const [autoSave, setAutoSave] = useState(true);
  const [criticalAlerts, setCriticalAlerts] = useState(true);
  const [analysisReports, setAnalysisReports] = useState(true);
  const [systemUpdates, setSystemUpdates] = useState(false);

  return (
    <div className="antialiased min-h-screen flex flex-col md:flex-row bg-background text-on-background selection:bg-primary-container selection:text-on-primary-container transition-colors duration-200">
      {/* Desktop Sidebar Navigation Drawer */}
      <SidebarNavigation />

      {/* Mobile TopAppBar */}
      <header className="md:hidden flex justify-between items-center w-full px-margin-mobile h-16 bg-surface border-b border-outline-variant sticky top-0 z-40">
        <button onClick={() => navigate('/dashboard')} className="text-on-surface p-2 rounded-full">
          <span className="material-symbols-outlined">menu</span>
        </button>
        <div className="font-headline-md text-headline-md font-bold text-on-surface tracking-tight">MachineSense</div>
        <button onClick={() => navigate('/analyze')} className="text-on-surface p-2 rounded-full">
          <span className="material-symbols-outlined">sensors</span>
        </button>
      </header>

      {/* Main Content Canvas */}
      <main className="flex-1 overflow-y-auto p-margin-mobile md:p-margin-desktop pb-24 md:pb-8 bg-background max-w-4xl mx-auto w-full">
        <div className="space-y-panel-gap">
          <h1 className="font-headline-lg text-headline-lg font-bold text-on-surface mb-6">Settings</h1>

          {/* Appearance Panel */}
          <section className="bg-surface-container border border-outline-variant rounded p-6">
            <h2 className="font-label-caps text-label-caps font-bold text-on-surface mb-4 uppercase tracking-widest">
              Appearance & Theme Architecture
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <button
                type="button"
                onClick={() => setTheme('light')}
                className={`flex flex-col items-center justify-center p-5 border rounded-lg cursor-pointer transition-all ${
                  theme === 'light'
                    ? 'border-primary-container bg-surface-container-high soft-cyan-glow font-bold'
                    : 'border-outline-variant bg-surface-container-low hover:bg-surface-container-high'
                }`}
              >
                <span className="material-symbols-outlined text-on-surface mb-2 text-3xl">light_mode</span>
                <span className="font-body-md text-body-md text-on-surface">Light Theme</span>
                <span className="font-data-sm text-[11px] text-on-surface-variant mt-1">Clean crisp white design tokens</span>
              </button>

              <button
                type="button"
                onClick={() => setTheme('dark')}
                className={`flex flex-col items-center justify-center p-5 border rounded-lg cursor-pointer transition-all ${
                  theme === 'dark'
                    ? 'border-primary-container bg-surface-container-high soft-cyan-glow font-bold'
                    : 'border-outline-variant bg-surface-container-low hover:bg-surface-container-high'
                }`}
              >
                <span className="material-symbols-outlined text-on-surface mb-2 text-3xl">dark_mode</span>
                <span className="font-body-md text-body-md text-on-surface">Dark Theme</span>
                <span className="font-data-sm text-[11px] text-on-surface-variant mt-1">High-contrast industrial dark mode</span>
              </button>
            </div>
          </section>

          {/* Analysis Preferences Panel */}
          <section className="bg-surface-container border border-outline-variant rounded p-6">
            <h2 className="font-label-caps text-label-caps font-bold text-on-surface mb-4 uppercase tracking-widest">
              Analysis Preferences
            </h2>
            <div className="space-y-6">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <div className="font-body-md text-body-md text-on-surface font-bold">Default Target Machine</div>
                  <div className="font-body-sm text-body-sm text-on-surface-variant">Select the primary asset for analysis pipeline.</div>
                </div>
                <select
                  value={targetMachine}
                  onChange={(e) => setTargetMachine(e.target.value)}
                  className="bg-surface-container-low border border-outline-variant text-on-surface rounded p-2 focus:border-primary-container font-data-sm text-data-sm w-full md:w-64 cursor-pointer font-bold"
                >
                  {machinesData.map((m) => (
                    <option key={m.id} value={m.id}>{m.id} — {m.name}</option>
                  ))}
                </select>
              </div>

              <div className="h-px bg-outline-variant/40 w-full"></div>

              <div className="flex items-center justify-between">
                <div>
                  <div className="font-body-md text-body-md text-on-surface font-bold">Auto-Save Results</div>
                  <div className="font-body-sm text-body-sm text-on-surface-variant">Automatically persist acoustic spectrum logs to SQLite database.</div>
                </div>
                <input
                  type="checkbox"
                  checked={autoSave}
                  onChange={() => setAutoSave(!autoSave)}
                  className="w-5 h-5 accent-primary-container cursor-pointer"
                />
              </div>
            </div>
          </section>

          {/* Notifications Panel */}
          <section className="bg-surface-container border border-outline-variant rounded p-6">
            <h2 className="font-label-caps text-label-caps text-on-surface mb-4 uppercase tracking-widest font-bold">
              Notifications
            </h2>
            <div className="space-y-4">
              <label className="flex items-start gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={criticalAlerts}
                  onChange={() => setCriticalAlerts(!criticalAlerts)}
                  className="mt-1 w-4 h-4 accent-primary-container cursor-pointer"
                />
                <div>
                  <div className="font-body-md text-body-md text-on-surface font-bold">Critical Alerts</div>
                  <div className="font-body-sm text-body-sm text-on-surface-variant">Immediate notifications for degrading machine signatures.</div>
                </div>
              </label>

              <label className="flex items-start gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={analysisReports}
                  onChange={() => setAnalysisReports(!analysisReports)}
                  className="mt-1 w-4 h-4 accent-primary-container cursor-pointer"
                />
                <div>
                  <div className="font-body-md text-body-md text-on-surface font-bold">Analysis Reports</div>
                  <div className="font-body-sm text-body-sm text-on-surface-variant">Daily summaries of asset health and spectral anomalies.</div>
                </div>
              </label>

              <label className="flex items-start gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={systemUpdates}
                  onChange={() => setSystemUpdates(!systemUpdates)}
                  className="mt-1 w-4 h-4 accent-primary-container cursor-pointer"
                />
                <div>
                  <div className="font-body-md text-body-md text-on-surface font-bold">System Updates</div>
                  <div className="font-body-sm text-body-sm text-on-surface-variant">Information regarding ML model updates and software versions.</div>
                </div>
              </label>
            </div>
          </section>

          {/* About Panel */}
          <section className="bg-surface-container border border-outline-variant rounded p-6">
            <h2 className="font-label-caps text-label-caps font-bold text-on-surface mb-4 uppercase tracking-widest">
              About MachineSense
            </h2>
            <div className="grid grid-cols-2 gap-y-4 font-data-sm text-data-sm">
              <div className="font-body-sm text-body-sm text-on-surface font-bold">Version</div>
              <div className="font-bold text-on-surface text-right md:text-left">PRL-4 Prototype</div>
              <div className="font-body-sm text-body-sm text-on-surface font-bold">Tech Stack</div>
              <div className="text-on-surface text-right md:text-left font-semibold">React, FastAPI, ML, SQLite</div>
            </div>
          </section>

          {/* Action Bar */}
          <div className="flex justify-end gap-4 mt-8">
            <button
              onClick={() => navigate('/dashboard')}
              className="px-4 py-2 bg-surface-container-high border border-outline-variant text-on-surface font-body-sm text-body-sm font-bold rounded hover:bg-surface-variant transition-colors cursor-pointer"
            >
              Discard Changes
            </button>
            <button
              onClick={() => navigate('/dashboard')}
              className="px-4 py-2 bg-primary-container text-on-primary-container font-body-sm text-body-sm rounded font-bold soft-cyan-glow transition-all hover:bg-primary-fixed cursor-pointer"
            >
              Save Configuration
            </button>
          </div>
        </div>
      </main>

      <BottomNavigation />
    </div>
  );
}
