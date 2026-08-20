import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import SidebarNavigation from '../components/layout/SidebarNavigation';
import BottomNavigation from '../components/layout/BottomNavigation';
import WaveformVisualizer from '../components/charts/WaveformVisualizer';
import { machinesData } from '../data/mockData';
import { API_URL } from '../config';

export default function Results() {
  const location = useLocation();
  const navigate = useNavigate();

  const analysisData = location.state?.analysisData;
  const machineId = location.state?.machineId || analysisData?.machine_id || 'id_00';
  const machine = machinesData.find((m) => m.id === machineId) || {
    id: machineId,
    name: analysisData?.machine_id ? `Asset (${analysisData.machine_id})` : 'MOTOR-01',
    type: 'Centrifugal Pump',
    location: 'Main Deck',
    healthScore: 94
  };

  const [showSpectrogramModal, setShowSpectrogramModal] = useState(false);

  const prediction = analysisData?.prediction || {
    label: 'no_machine_sound',
    class: -1,
    abnormal_probability: 0.0,
    normal_probability: 0.0,
    status: 'NO_MACHINE_SOUND'
  };

  const audio = analysisData?.audio || { duration: 10.0, sample_rate: 16000 };
  const signal = analysisData?.signal || { rms: 0.042, signal_quality: 'good' };
  const frequency = analysisData?.frequency || { dominant_frequency_hz: 4200 };
  const spectral = analysisData?.spectral_features || { centroid_hz: 2028.3, flatness: 0.0957 };

  const labelUpper = (prediction.label || 'NO_MACHINE_SOUND').toUpperCase();
  const isNoMachineSound = labelUpper === 'NO_MACHINE_SOUND' || prediction.status === 'NO_MACHINE_SOUND';
  const isNormal = labelUpper === 'NORMAL' && !isNoMachineSound;
  const isAbnormal = labelUpper === 'ABNORMAL' || labelUpper === 'CRITICAL';

  const abnormalProbPct = (prediction.abnormal_probability * 100).toFixed(1);
  const normalProbPct = (prediction.normal_probability * 100).toFixed(1);
  const confidencePct = (Math.max(prediction.normal_probability, prediction.abnormal_probability) * 100).toFixed(1);
  const anomalyScore = (prediction.abnormal_probability || 0.12).toFixed(2);

  useEffect(() => {
    if (!analysisData) {
      console.warn("No analysis data found on /results, redirecting to /analyze.");
      navigate('/analyze', { replace: true });
    } else {
      console.log("Analysis Results Loaded - Machine ID:", machine.id, "Label:", labelUpper);
    }
  }, [analysisData, machine.id, labelUpper, navigate]);

  if (!analysisData) {
    return null;
  }

  return (
    <div className="antialiased min-h-screen flex flex-col md:flex-row bg-background text-on-background selection:bg-primary-container selection:text-on-primary-container transition-colors duration-200">
      {/* Desktop Sidebar Navigation */}
      <SidebarNavigation />

      {/* Mobile Header */}
      <header className="md:hidden flex justify-between items-center w-full px-margin-mobile h-16 bg-surface border-b border-outline-variant sticky top-0 z-40">
        <button onClick={() => navigate('/dashboard')} className="text-on-surface p-2 rounded-full">
          <span className="material-symbols-outlined">menu</span>
        </button>
        <h1 className="font-headline-md text-headline-md font-bold text-on-surface tracking-tight">MachineSense</h1>
        <button onClick={() => navigate('/analyze')} className="text-on-surface p-2 rounded-full">
          <span className="material-symbols-outlined">sensors</span>
        </button>
      </header>

      {/* Main Content Canvas */}
      <main className="flex-1 p-margin-mobile md:p-margin-desktop overflow-x-hidden flex flex-col gap-panel-gap pb-24 md:pb-margin-desktop w-full max-w-7xl mx-auto">
        {/* Header Section */}
        <header className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-2">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className={`h-2 w-2 rounded-full ${isNoMachineSound ? 'bg-outline' : isNormal ? 'bg-secondary pulse-dot' : 'bg-error pulse-dot'}`}></span>
              <span className={`font-data-sm text-data-sm font-bold tracking-widest uppercase ${isNoMachineSound ? 'text-on-surface-variant' : isNormal ? 'text-secondary' : 'text-error'}`}>
                {isNoMachineSound ? 'INPUT VALIDATION • INSUFFICIENT SIGNAL' : 'System Online'}
              </span>
            </div>
            <h2 className="font-headline-lg text-headline-lg text-on-surface font-bold">Analysis Complete</h2>
            <p className="font-body-md text-body-md text-on-surface-variant mt-1">
              Machine: <span className="font-data-lg text-data-lg text-on-surface ml-2 font-bold">{machine.id}</span>
            </p>
          </div>

          {/* Pipeline Status Nodes */}
          <div className="flex items-center gap-2 bg-surface-container-low p-3 rounded-lg border border-outline-variant">
            <div className="flex flex-col items-center">
              <div className="w-6 h-6 rounded-full bg-surface-container-high flex items-center justify-center border border-outline-variant">
                <span className="material-symbols-outlined text-[14px] text-on-surface">sensors</span>
              </div>
              <span className="font-label-caps text-label-caps text-on-surface mt-1 font-bold">Capture</span>
            </div>
            <div className="w-8 h-px bg-outline-variant"></div>
            <div className="flex flex-col items-center">
              <div className="w-6 h-6 rounded-full bg-surface-container-high flex items-center justify-center border border-outline-variant">
                <span className="material-symbols-outlined text-[14px] text-on-surface">memory</span>
              </div>
              <span className="font-label-caps text-label-caps text-on-surface mt-1 font-bold">Process</span>
            </div>
            <div className="w-8 h-px bg-outline-variant"></div>
            <div className="flex flex-col items-center">
              <div className={`w-6 h-6 rounded-full flex items-center justify-center ${isNoMachineSound ? 'bg-surface-container-high border border-outline-variant' : 'bg-primary-container soft-cyan-glow'}`}>
                <span className="material-symbols-outlined text-[14px] font-bold">{isNoMachineSound ? 'warning' : 'check'}</span>
              </div>
              <span className="font-label-caps text-label-caps text-on-surface mt-1 font-bold">Analyze</span>
            </div>
          </div>
        </header>

        {/* Main Status Hero Banner */}
        <section className="bg-surface-container rounded-lg border border-outline-variant overflow-hidden relative">
          <div className={`absolute inset-0 bg-gradient-to-r ${isNoMachineSound ? 'from-surface-container-high/40' : isNormal ? 'from-secondary/10' : 'from-error/10'} to-transparent pointer-events-none`}></div>
          <div className="p-6 md:p-8 flex flex-col md:flex-row items-center justify-between gap-6 relative z-10">
            <div className="flex items-center gap-6">
              <div className={`w-20 h-20 rounded-full border-4 ${isNoMachineSound ? 'border-outline bg-surface-container-high' : isNormal ? 'border-secondary bg-secondary/10' : 'border-error bg-error/10'} flex items-center justify-center`}>
                <span className={`material-symbols-outlined text-[40px] ${isNoMachineSound ? 'text-on-surface-variant' : isNormal ? 'text-secondary' : 'text-error'}`}>
                  {isNoMachineSound ? 'volume_off' : isNormal ? 'check_circle' : 'warning'}
                </span>
              </div>
              <div>
                <h3 className={`font-headline-lg text-headline-lg uppercase tracking-wider mb-2 font-bold ${isNoMachineSound ? 'text-on-surface-variant' : isNormal ? 'text-secondary' : 'text-error'}`}>
                  {isNoMachineSound ? 'No Machine Sound Detected' : isNormal ? 'Normal Status' : 'Abnormal Anomaly'}
                </h3>
                {isNoMachineSound ? (
                  <p className="font-body-md text-body-md text-on-surface max-w-xl font-medium">
                    No sufficient machine acoustic signal detected in this recording. Please ensure the target machine is operating and record again.
                  </p>
                ) : (
                  <div className="flex gap-4">
                    <div className="bg-surface-container-low px-3 py-1.5 rounded border border-outline-variant">
                      <span className="font-label-caps text-label-caps text-on-surface-variant block mb-1 font-bold">Anomaly Score</span>
                      <span className="font-data-lg text-data-lg text-on-surface font-bold">{anomalyScore} <span className="font-data-sm text-data-sm text-on-surface-variant">/ 1.0</span></span>
                    </div>
                    <div className="bg-surface-container-low px-3 py-1.5 rounded border border-outline-variant">
                      <span className="font-label-caps text-label-caps text-on-surface-variant block mb-1 font-bold">Confidence</span>
                      <span className="font-data-lg text-data-lg text-on-surface font-bold">{confidencePct}<span className="font-data-sm text-data-sm text-on-surface-variant">%</span></span>
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="w-full md:w-auto grid grid-cols-2 md:grid-cols-1 gap-3">
              {isNoMachineSound ? (
                <button
                  onClick={() => navigate('/analyze')}
                  className="bg-primary-container text-on-primary-container font-body-sm text-body-sm font-bold py-2.5 px-6 rounded transition-all soft-cyan-glow flex items-center justify-center gap-2 cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[18px]">mic</span>
                  Record Again
                </button>
              ) : (
                <button
                  onClick={() => window.print()}
                  className="bg-primary-container text-on-primary-container font-body-sm text-body-sm font-bold py-2 px-6 rounded transition-all soft-cyan-glow flex items-center justify-center gap-2 cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[18px]">save</span>
                  Save Analysis
                </button>
              )}
              <button
                onClick={() => navigate('/history')}
                className="bg-surface-container-high border border-outline-variant hover:bg-surface-variant text-on-surface font-body-sm text-body-sm font-bold py-2 px-6 rounded transition-colors flex items-center justify-center gap-2 cursor-pointer"
              >
                <span className="material-symbols-outlined text-[18px]">history</span>
                View History
              </button>
            </div>
          </div>
        </section>

        {/* Detailed Metrics Bento Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-panel-gap">
          {/* AI Probability Probabilities / Validity Assessment */}
          <div className="tech-border bg-surface-container rounded-lg p-6 flex flex-col justify-between gap-4">
            <span className="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-widest border-b border-outline-variant pb-2 font-bold">
              {isNoMachineSound ? 'Acoustic Signal Validity' : 'Class Probabilities'}
            </span>

            {isNoMachineSound ? (
              <div className="space-y-3 font-data-sm text-data-sm">
                <div className="p-3 bg-surface-container-low border border-outline-variant rounded">
                  <span className="text-on-surface-variant text-[10px] uppercase block font-bold">Signal Gate Result</span>
                  <span className="text-error font-bold">INSUFFICIENT ACOUSTIC ENERGY</span>
                </div>
                <div className="p-3 bg-surface-container-low border border-outline-variant rounded">
                  <span className="text-on-surface-variant text-[10px] uppercase block font-bold">ML Classifier Status</span>
                  <span className="text-on-surface-variant font-semibold">BYPASSED (No Random Forest call)</span>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between font-data-sm text-data-sm mb-1">
                    <span className="text-on-surface font-semibold">Normal Probability</span>
                    <span className="text-secondary font-bold">{normalProbPct}%</span>
                  </div>
                  <div className="w-full bg-surface-container-high h-2 rounded-full overflow-hidden">
                    <div className="bg-secondary h-full rounded-full" style={{ width: `${normalProbPct}%` }}></div>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between font-data-sm text-data-sm mb-1">
                    <span className="text-on-surface font-semibold">Abnormal Probability</span>
                    <span className={`font-bold ${prediction.abnormal_probability > 0.4 ? 'text-error' : 'text-on-surface-variant'}`}>{abnormalProbPct}%</span>
                  </div>
                  <div className="w-full bg-surface-container-high h-2 rounded-full overflow-hidden">
                    <div className={`h-full rounded-full ${prediction.abnormal_probability > 0.4 ? 'bg-error' : 'bg-on-surface-variant'}`} style={{ width: `${abnormalProbPct}%` }}></div>
                  </div>
                </div>
              </div>
            )}

            <div className="pt-2 border-t border-outline-variant/30 font-data-sm text-data-sm text-on-surface-variant text-xs font-semibold">
              Result Status: <strong className="text-on-surface">{isNoMachineSound ? 'NO_MACHINE_SOUND' : prediction.label.toUpperCase()}</strong>
            </div>
          </div>

          {/* Acoustic Telemetry Diagnostics */}
          <div className="tech-border bg-surface-container rounded-lg p-6 flex flex-col justify-between gap-3 md:col-span-2">
            <span className="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-widest border-b border-outline-variant pb-2 font-bold flex justify-between items-center">
              <span>Acoustic Signal Telemetry</span>
              <span className="material-symbols-outlined text-[18px]">query_stats</span>
            </span>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 font-data-sm text-data-sm">
              <div className="bg-surface-container-low border border-outline-variant/30 p-3 rounded">
                <span className="text-on-surface-variant text-[10px] uppercase block font-semibold">Dominant Frequency</span>
                <span className="text-on-surface text-base font-bold">{frequency.dominant_frequency_hz} Hz</span>
              </div>
              <div className="bg-surface-container-low border border-outline-variant/30 p-3 rounded">
                <span className="text-on-surface-variant text-[10px] uppercase block font-semibold">Signal Quality</span>
                <span className={`text-base font-bold uppercase ${isNoMachineSound ? 'text-error' : 'text-secondary'}`}>{signal.signal_quality}</span>
              </div>
              <div className="bg-surface-container-low border border-outline-variant/30 p-3 rounded">
                <span className="text-on-surface-variant text-[10px] uppercase block font-semibold">Raw RMS Energy</span>
                <span className="text-on-surface text-base font-bold">{signal.rms || 0.042}</span>
              </div>
              <div className="bg-surface-container-low border border-outline-variant/30 p-3 rounded">
                <span className="text-on-surface-variant text-[10px] uppercase block font-semibold">Sample Rate</span>
                <span className="text-on-surface text-base font-bold">{audio.sample_rate} Hz</span>
              </div>
              <div className="bg-surface-container-low border border-outline-variant/30 p-3 rounded">
                <span className="text-on-surface-variant text-[10px] uppercase block font-semibold">Duration</span>
                <span className="text-on-surface text-base font-bold">{audio.duration} s</span>
              </div>
              <div className="bg-surface-container-low border border-outline-variant/30 p-3 rounded">
                <span className="text-on-surface-variant text-[10px] uppercase block font-semibold">Spectral Centroid</span>
                <span className="text-on-surface text-base font-bold">{spectral.centroid_hz} Hz</span>
              </div>
            </div>
          </div>
        </div>

        {/* AI Assessment & Recommendation Panel */}
        <section className="tech-border bg-surface-container rounded-lg p-6 flex flex-col md:flex-row gap-6 items-center justify-between">
          <div className="flex-1 space-y-3">
            <span className="font-label-caps text-label-caps text-on-surface uppercase tracking-widest font-bold flex items-center gap-2">
              <span className="material-symbols-outlined text-[18px]">memory</span>
              AI DIAGNOSTIC ASSESSMENT & RECOMMENDATIONS
            </span>

            <p className="font-body-md text-body-md text-on-surface leading-relaxed">
              {isNoMachineSound
                ? 'No sufficient machine sound was detected in the input signal. Silence or ambient background room noise cannot be classified as a healthy operating machine.'
                : isNormal
                ? 'Acoustic frequency spectrum matches normal operating baseline. No harmonic distortions or bearing failure frequencies detected.'
                : 'WARNING: Significant acoustic anomaly detected. Spectral energy shifts indicate potential mechanical fault or bearing degradation.'
              }
            </p>
            <p className="font-data-sm text-data-sm text-on-surface-variant border-l-2 border-primary-container pl-3 py-1 font-medium">
              <strong>Action Item:</strong> {isNoMachineSound
                ? 'Ensure the target machinery is running at standard operating speed, hold microphone 10–15cm from housing, and re-record.'
                : isNormal
                ? 'Continue regular operation. Next scheduled acoustic inspection in 14 days.'
                : 'Schedule immediate physical inspection. Check motor alignment, bearing lubrication, and mounting stability.'
              }
            </p>
          </div>

          <div className="w-full md:w-96">
            <WaveformVisualizer samples={analysisData?.waveform?.samples || []} />
          </div>
        </section>

        {/* Log-Mel Spectrogram Analysis Panel */}
        {analysisData?.spectrogram?.url && (
          <section className="tech-border bg-surface-container rounded-lg p-6 flex flex-col gap-4">
            <div className="flex justify-between items-center border-b border-outline-variant pb-2">
              <span className="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-widest font-bold flex items-center gap-2">
                <span className="material-symbols-outlined text-[18px] text-primary-fixed-dim">graphic_eq</span>
                Log-Mel Acoustic Spectrogram
              </span>
              <span className="font-data-sm text-data-sm text-on-surface-variant font-mono">168 Mel Bins • dB Power Scale</span>
            </div>

            <div className="rounded border border-outline-variant bg-[#0d1516] flex items-center justify-center p-2 overflow-hidden">
              <img
                src={`${API_URL}${analysisData.spectrogram.url}`}
                alt="Log-Mel Spectrogram"
                className="w-full h-auto object-contain max-h-[360px] rounded"
              />
            </div>
          </section>
        )}

        {/* Bottom Actions Row */}
        <div className="flex flex-col sm:flex-row gap-4 justify-end">
          <button
            onClick={() => navigate('/analyze')}
            className="bg-primary-container text-on-primary-container font-body-sm text-body-sm font-bold py-3 px-6 rounded soft-cyan-glow hover:bg-primary-fixed transition-all cursor-pointer flex items-center justify-center gap-2"
          >
            <span className="material-symbols-outlined text-[18px]">mic</span>
            Record / Analyze Another Machine
          </button>
        </div>

        {/* Log-Mel Spectrogram Modal */}
        {showSpectrogramModal && analysisData?.spectrogram?.url && (
          <div className="fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center p-4">
            <div className="bg-surface-container border border-outline-variant p-6 rounded-lg max-w-3xl w-full flex flex-col gap-4 relative">
              <div className="flex justify-between items-center border-b border-outline-variant pb-3">
                <h3 className="font-headline-md text-headline-md text-on-surface font-bold flex items-center gap-2">
                  <span className="material-symbols-outlined">graphic_eq</span>
                  Log-Mel Spectrogram Visualization
                </h3>
                <button
                  onClick={() => setShowSpectrogramModal(false)}
                  className="w-8 h-8 rounded bg-surface-container-high flex items-center justify-center text-on-surface hover:bg-surface-variant cursor-pointer"
                >
                  <span className="material-symbols-outlined text-lg">close</span>
                </button>
              </div>

              <div className="rounded border border-outline-variant bg-black flex items-center justify-center p-2">
                <img
                  src={`${API_URL}${analysisData.spectrogram.url}`}
                  alt="Log-Mel Spectrogram"
                  className="w-full h-auto object-contain max-h-[360px]"
                />
              </div>

              <div className="flex justify-end">
                <button
                  onClick={() => setShowSpectrogramModal(false)}
                  className="px-6 py-2 rounded bg-primary-container text-on-primary-container font-body-sm text-body-sm font-bold hover:bg-primary-fixed cursor-pointer"
                >
                  Close Viewer
                </button>
              </div>
            </div>
          </div>
        )}
      </main>

      <BottomNavigation />
    </div>
  );
}
