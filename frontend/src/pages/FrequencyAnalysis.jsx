import React, { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import TopNavigation from '../components/layout/TopNavigation';
import BottomNavigation from '../components/layout/BottomNavigation';
import { machinesData } from '../data/mockData';

export default function FrequencyAnalysis() {
  const [searchParams] = useSearchParams();
  const machineId = searchParams.get('machine') || 'id_00';
  const machine = machinesData.find((m) => m.id === machineId) || machinesData[0];

  const [activeTab, setActiveTab] = useState('Frequency');

  // Generate 60 FFT spectrum bars with specific peak highlights
  const fftBars = Array.from({ length: 60 }).map((_, i) => {
    let height = Math.floor(Math.sin(i * 0.3) * 20 + Math.cos(i * 0.7) * 15 + 35);
    let isPeak = false;
    let label = '';

    if (i === 15) {
      height = 85;
      isPeak = true;
      label = '800Hz';
    } else if (i === 30) {
      height = 95;
      isPeak = true;
      label = machine.dominantFreq || '1.62kHz';
    } else if (i === 50) {
      height = 75;
      isPeak = true;
      label = '3.24kHz';
    }

    return { id: i, height: Math.max(8, height), isPeak, label };
  });

  return (
    <div className="bg-background text-on-surface antialiased min-h-screen flex flex-col pt-16 pb-24 md:pb-8 font-body-md selection:bg-primary-container selection:text-on-primary-container">
      <TopNavigation />

      <main className="flex-grow flex flex-col w-full max-w-7xl mx-auto px-margin-mobile md:px-margin-desktop py-panel-gap gap-panel-gap">
        {/* Header Section */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 border-b border-outline-variant pb-4">
          <div>
            <h1 className="font-headline-lg text-headline-lg text-on-surface font-bold">
              Frequency STFT & Spectral Breakdown
            </h1>
            <p className="font-data-sm text-data-sm text-on-surface-variant mt-1">
              TARGET ASSET: <strong className="text-primary-fixed-dim">{machine.id} ({machine.name})</strong> • SAMPLING: 16 kHz PCM • SENSOR: VIB-4A
            </p>
          </div>

          {/* View Mode Switcher */}
          <div className="flex bg-surface-container-low border border-outline-variant p-1 rounded">
            {['Waveform', 'Frequency', 'Spectrogram'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-1.5 rounded font-label-caps text-label-caps uppercase transition-all cursor-pointer ${
                  activeTab === tab
                    ? 'text-on-primary-container bg-primary-container font-bold soft-cyan-glow'
                    : 'text-on-surface-variant hover:text-on-surface'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        {/* Bento Grid Layout */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-panel-gap flex-grow">
          {/* Main Spectrum Visualizer */}
          <section className="tech-border bg-surface-container rounded-lg p-6 md:col-span-8 flex flex-col justify-between relative overflow-hidden technical-grid">
            <div className="flex justify-between items-center mb-6 relative z-10 border-b border-outline-variant/30 pb-3">
              <span className="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-widest font-bold flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-secondary pulse-dot"></span>
                LIVE FFT SPECTRUM DECOMPOSITION
              </span>
              <div className="flex items-center gap-4 font-data-sm text-data-sm text-on-surface-variant text-xs">
                <div className="flex items-center gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-sm bg-primary-fixed-dim opacity-30 border border-primary-fixed-dim"></div>
                  <span>Noise Floor</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-sm bg-primary-container soft-cyan-glow"></div>
                  <span className="text-primary-fixed-dim font-bold">Dominant Peak</span>
                </div>
              </div>
            </div>

            {/* FFT Graph Bars */}
            <div className="flex-grow flex items-end justify-between gap-1 relative z-10 h-64 border-l border-b border-outline-variant/50 pb-2 pl-2 mt-4">
              <div className="absolute -left-8 top-0 h-full flex flex-col justify-between font-data-sm text-data-sm text-on-surface-variant text-[10px] pointer-events-none">
                <span>-10dB</span>
                <span>-30dB</span>
                <span>-50dB</span>
                <span>-70dB</span>
              </div>

              {fftBars.map((bar) => (
                <div key={bar.id} className="relative w-full flex flex-col justify-end group h-full">
                  <div
                    className={`w-full rounded-t transition-all ${
                      bar.isPeak
                        ? 'bg-primary-container border-t-2 border-primary-fixed soft-cyan-glow'
                        : 'bg-primary-fixed-dim/20 hover:bg-primary-fixed-dim/40'
                    }`}
                    style={{ height: `${bar.height}%`, minHeight: '4px' }}
                  />
                  {bar.isPeak && (
                    <div className="absolute -top-6 left-1/2 -translate-x-1/2 font-data-sm text-[10px] text-primary-fixed-dim whitespace-nowrap font-bold">
                      {bar.label}
                    </div>
                  )}
                </div>
              ))}

              <div className="absolute -bottom-6 left-0 w-full flex justify-between font-data-sm text-data-sm text-on-surface-variant text-[10px]">
                <span>0Hz</span>
                <span>1kHz</span>
                <span>2kHz</span>
                <span>4kHz</span>
                <span>8kHz</span>
              </div>
            </div>
          </section>

          {/* Telemetry Sidebar */}
          <section className="flex flex-col gap-panel-gap md:col-span-4">
            {/* Signal Metrics Card */}
            <div className="tech-border bg-surface-container rounded-lg p-6 flex flex-col gap-3">
              <span className="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-widest border-b border-outline-variant pb-2 font-bold">
                SIGNAL TELEMETRY
              </span>
              <div className="flex flex-col gap-3 font-data-sm text-data-sm">
                <div className="flex justify-between items-center border-b border-outline-variant/30 pb-2">
                  <span className="text-on-surface-variant">Signal-to-Noise (SNR)</span>
                  <span className="text-secondary font-bold">28 dB (GOOD)</span>
                </div>
                <div className="flex justify-between items-center border-b border-outline-variant/30 pb-2">
                  <span className="text-on-surface-variant">Stability Rating</span>
                  <span className="text-secondary font-bold">{machine.stability || '98.5%'}</span>
                </div>
                <div className="flex justify-between items-center border-b border-outline-variant/30 pb-2">
                  <span className="text-on-surface-variant">Clipping Events</span>
                  <span className="text-on-surface font-semibold">0 (Last 1hr)</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-on-surface-variant">Sampling Rate</span>
                  <span className="text-on-surface font-semibold">16 kHz PCM</span>
                </div>
              </div>
            </div>

            {/* Harmonic Diagnostic */}
            <div className="tech-border bg-surface-container rounded-lg p-6 flex-grow flex flex-col justify-between gap-4">
              <div>
                <span className="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-widest border-b border-outline-variant pb-2 block font-bold">
                  HARMONIC ASSESSMENT
                </span>
                <div className="flex flex-col items-center text-center gap-3 my-4">
                  <div className="w-14 h-14 rounded bg-surface-container-high flex items-center justify-center border border-outline-variant text-primary-fixed-dim soft-cyan-glow">
                    <span className="material-symbols-outlined text-3xl">troubleshoot</span>
                  </div>
                  <div>
                    <h3 className="font-headline-md text-body-lg text-on-surface font-bold mb-1">
                      {machine.status === 'Healthy' || machine.status === 'Normal' ? 'Optimal Acoustic Balance' : 'Bearing Wear Indication'}
                    </h3>
                    <p className="font-data-sm text-data-sm text-on-surface-variant text-xs leading-relaxed">
                      Dominant peak at {machine.dominantFreq || '450 Hz'} matches baseline operating signature for machine asset model SKF-6204.
                    </p>
                  </div>
                </div>
              </div>

              <button
                onClick={() => window.print()}
                className="w-full py-3 bg-primary-container text-on-primary-container font-body-sm text-body-sm font-bold rounded soft-cyan-glow hover:bg-primary-fixed transition-all flex items-center justify-center gap-2 cursor-pointer"
              >
                <span className="material-symbols-outlined text-base">summarize</span>
                Export Full Spectrum Report
              </button>
            </div>
          </section>
        </div>
      </main>

      <BottomNavigation />
    </div>
  );
}

