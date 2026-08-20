import React from 'react';
import { useNavigate } from 'react-router-dom';
import SidebarNavigation from '../components/layout/SidebarNavigation';
import BottomNavigation from '../components/layout/BottomNavigation';

export default function ResearchInsights() {
  const navigate = useNavigate();

  return (
    <div className="antialiased min-h-screen flex flex-col md:flex-row bg-background text-on-background selection:bg-primary-container selection:text-on-primary-container">
      {/* Desktop Navigation Drawer */}
      <SidebarNavigation />

      {/* Mobile Top App Bar */}
      <header className="md:hidden flex justify-between items-center w-full px-margin-mobile h-16 bg-surface border-b border-outline-variant shrink-0 sticky top-0 z-40">
        <button onClick={() => navigate('/dashboard')} className="text-primary-fixed-dim p-2 rounded-full">
          <span className="material-symbols-outlined">menu</span>
        </button>
        <h1 className="font-headline-md text-headline-md font-bold text-primary-fixed-dim tracking-tight">MachineSense</h1>
        <button onClick={() => navigate('/analyze')} className="text-primary-fixed-dim p-2 rounded-full">
          <span className="material-symbols-outlined">sensors</span>
        </button>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto p-margin-mobile md:p-margin-desktop bg-background pb-24 md:pb-margin-desktop w-full max-w-7xl mx-auto">
        <header className="mb-8 border-b border-outline-variant pb-4">
          <h2 className="font-headline-lg text-headline-lg text-on-surface mb-2 font-bold">Research Insights</h2>
          <p className="font-body-md text-body-md text-on-surface-variant">Technical validation and prototype evaluation metrics based on MIMII dataset analysis.</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-12 gap-panel-gap">
          {/* Key Metrics Overview Bento Grid */}
          <div className="col-span-1 md:col-span-12 grid grid-cols-1 md:grid-cols-3 gap-panel-gap">
            {/* Machine Dependence */}
            <div className="bg-surface-container-low border border-outline-variant rounded p-6 relative overflow-hidden group hover:border-outline transition-colors shadow-sm">
              <div className="absolute top-4 right-4 w-2.5 h-2.5 rounded-full bg-secondary soft-cyan-glow"></div>
              <h3 className="font-label-caps text-label-caps text-on-surface-variant mb-4 tracking-widest uppercase font-bold">Machine Dependence</h3>
              <div className="flex items-end gap-2">
                <span className="font-data-lg text-4xl font-bold text-primary-fixed-dim">99.76</span>
                <span className="font-data-sm text-data-sm text-on-surface-variant mb-1 font-bold">% Accuracy</span>
              </div>
              <p className="font-body-sm text-body-sm text-on-surface-variant mt-4 leading-relaxed">Baseline performance metric on isolated machine environments.</p>
            </div>

            {/* Generalization */}
            <div className="bg-surface-container-low border border-outline-variant rounded p-6 relative overflow-hidden group hover:border-outline transition-colors shadow-sm">
              <div className="absolute top-4 right-4 w-2.5 h-2.5 rounded-full bg-secondary soft-cyan-glow"></div>
              <h3 className="font-label-caps text-label-caps text-on-surface-variant mb-4 tracking-widest uppercase font-bold">Generalization</h3>
              <div className="flex items-center gap-3">
                <span className="material-symbols-outlined text-primary-fixed-dim text-4xl">model_training</span>
                <span className="font-headline-md text-headline-md text-primary-fixed-dim font-bold">LOMO Eval</span>
              </div>
              <p className="font-body-sm text-body-sm text-on-surface-variant mt-4 leading-relaxed">Leave-One-Machine-Out validation strategy confirming model robustness.</p>
            </div>

            {/* Model Comparison */}
            <div className="bg-surface-container-low border border-outline-variant rounded p-6 relative overflow-hidden group hover:border-outline transition-colors shadow-sm">
              <div className="absolute top-4 right-4 w-2.5 h-2.5 rounded-full bg-primary-container soft-cyan-glow"></div>
              <h3 className="font-label-caps text-label-caps text-on-surface-variant mb-4 tracking-widest uppercase font-bold">Primary Architecture</h3>
              <div className="flex flex-col gap-1">
                <span className="font-headline-md text-headline-md text-primary-fixed-dim font-bold">Machine-Invariant RF</span>
                <span className="font-body-sm text-body-sm text-error font-medium">vs CNN / Autoencoder</span>
              </div>
              <p className="font-body-sm text-body-sm text-on-surface-variant mt-4 leading-relaxed">Random Forest selected for superior operational stability.</p>
            </div>
          </div>
        </div>
      </main>

      <BottomNavigation />
    </div>
  );
}
