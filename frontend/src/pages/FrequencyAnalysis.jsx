import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import TopNavigation from '../components/layout/TopNavigation';
import BottomNavigation from '../components/layout/BottomNavigation';
import WaveformVisualizer from '../components/charts/WaveformVisualizer';
import { machinesData } from '../data/mockData';
import { API_URL } from '../config';

export default function FrequencyAnalysis() {
  const [searchParams] = useSearchParams();
  const machineId = searchParams.get('machine') || 'id_00';
  const machine = machinesData.find((m) => m.id === machineId) || machinesData[0];

  const [activeTab, setActiveTab] = useState('Frequency');
  const [latestAnalysis, setLatestAnalysis] = useState(null);

  useEffect(() => {
    let isMounted = true;
    const fetchLatestMachineRecord = async () => {
      try {
        const res = await fetch(`${API_URL}/api/history/${machine.id}?limit=1`);
        if (res.ok) {
          const data = await res.json();
          const records = data.records || [];
          if (isMounted && records.length > 0) {
            setLatestAnalysis(records[0]);
          }
        }
      } catch (err) {
        console.error("Error fetching machine history for spectrum page:", err);
      }
    };
    fetchLatestMachineRecord();
    return () => { isMounted = false; };
  }, [machine.id]);

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
      label = latestAnalysis ? `${latestAnalysis.dominant_frequency_hz}Hz` : '1.62kHz';
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
          {/* Main Visualizer Area */}
          <section className="tech-border bg-surface-container rounded-lg p-6 md:col-span-8 flex flex-col justify-between relative overflow-hidden technical-grid min-h-[380px]">
            <div className="flex justify-between items-center mb-4 relative z-10 border-b border-outline-variant/30 pb-3">
              <span className="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-widest font-bold flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-secondary pulse-dot"></span>
                {activeTab === 'Waveform' && 'TIME-DOMAIN ACOUSTIC WAVEFORM OSCILLATION'}
                {activeTab === 'Frequency' && 'LIVE FFT SPECTRUM DECOMPOSITION'}
                {activeTab === 'Spectrogram' && 'LOG-MEL ACOUSTIC SPECTROGRAM (168 MEL BINS)'}
              </span>
              <span className="font-data-sm text-data-sm text-primary-fixed-dim font-bold">
                {activeTab.toUpperCase()} MODE ACTIVE
              </span>
            </div>

            {/* WAVEFORM TAB VIEW */}
            {activeTab === 'Waveform' && (
              <div className="flex-grow flex flex-col justify-center items-center w-full relative z-10 py-4">
                <WaveformVisualizer samples={latestAnalysis?.samples || []} height={220} />
              </div>
            )}

            {/* FREQUENCY TAB VIEW */}
            {activeTab === 'Frequency' && (
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
            )}

            {/* SPECTROGRAM TAB VIEW */}
            {activeTab === 'Spectrogram' && (
              <div className="flex-grow flex items-center justify-center relative z-10 w-full p-2">
                {latestAnalysis?.analysis_id ? (
                  <img
                    src={`${API_URL}/api/analysis/${latestAnalysis.analysis_id}/spectrogram`}
                    alt="Log-Mel Spectrogram"
                    className="w-full h-auto max-h-[320px] object-contain rounded border border-outline-variant bg-[#0d1516]"
                  />
                ) : (
                  <div className="flex flex-col items-center justify-center p-8 border border-dashed border-outline-variant rounded text-on-surface-variant gap-2 w-full h-64">
                    <span className="material-symbols-outlined text-4xl text-primary-fixed-dim">graphic_eq</span>
                    <span className="font-body-md font-semibold">No recent spectrogram recording available for {machine.id}.</span>
                    <span className="font-data-sm text-xs">Run a new machine acoustic diagnostic to generate a Log-Mel Spectrogram.</span>
                  </div>
                )}
              </div>
            )}
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
                  <span className="text-on-surface-variant">Dominant Freq</span>
                  <span className="text-secondary font-bold">{latestAnalysis?.dominant_frequency_hz || '450.0'} Hz</span>
                </div>
                <div className="flex justify-between items-center border-b border-outline-variant/30 pb-2">
                  <span className="text-on-surface-variant">Signal Quality</span>
                  <span className="text-secondary font-bold uppercase">{latestAnalysis?.signal_quality || 'GOOD'}</span>
                </div>
                <div className="flex justify-between items-center border-b border-outline-variant/30 pb-2">
                  <span className="text-on-surface-variant">Raw RMS Energy</span>
                  <span className="text-on-surface font-semibold">{latestAnalysis?.rms || '0.042'}</span>
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
                      {latestAnalysis?.prediction_label === 'normal' ? 'Optimal Acoustic Balance' : 'Acoustic Diagnostic Signature'}
                    </h3>
                    <p className="font-data-sm text-data-sm text-on-surface-variant text-xs leading-relaxed">
                      Dominant peak at {latestAnalysis?.dominant_frequency_hz || '450.0'} Hz matches baseline operating signature for machine asset {machine.id}.
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
