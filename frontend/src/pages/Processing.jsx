import React, { useEffect, useState, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import TopNavigation from '../components/layout/TopNavigation';
import BottomNavigation from '../components/layout/BottomNavigation';
import AmbientShader from '../components/layout/AmbientShader';
import { machinesData } from '../data/mockData';
import { API_URL } from '../config';
import { getActiveAudioFile, clearActiveAudioFile } from '../utils/audioStore';

export default function Processing() {
  const location = useLocation();
  const navigate = useNavigate();

  // Retrieve File object safely from memory store or location.state fallback
  const rawFile = getActiveAudioFile() || location.state?.rawFile;
  const machineId = location.state?.machineId || 'id_00';
  const machine = machinesData.find((m) => m.id === machineId) || machinesData[0];

  const [activeStep, setActiveStep] = useState(0); // 0..4
  const [errorMessage, setErrorMessage] = useState(null);
  const [retryTrigger, setRetryTrigger] = useState(0);

  // Single-execution latch ref across React 18 mounts/re-renders
  const hasDispatchedRef = useRef(false);
  const requestIdRef = useRef(null);
  const componentAliveRef = useRef(true);

  // Generate a single unique request_id per processing attempt
  if (!requestIdRef.current) {
    requestIdRef.current = `req_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
  }

  useEffect(() => {
    componentAliveRef.current = true;

    // Prevent duplicate fetch execution during React 18 StrictMode double-mount
    if (hasDispatchedRef.current) {
      console.log('Processing: fetch already dispatched for this session, skipping duplicate run.');
      return;
    }
    hasDispatchedRef.current = true;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 25000); // 25s timeout guard

    const executeAnalysis = async () => {
      try {
        setErrorMessage(null);

        if (!rawFile || !(rawFile instanceof Blob || rawFile instanceof File)) {
          console.error("Audio Processing Error: rawFile is invalid or missing:", rawFile);
          throw new Error('No valid audio file selected. Please return to upload and choose a WAV recording.');
        }

        // STEP 1: Audio Selected & Captured
        console.log('STEP 1: file selected', rawFile.name, rawFile.size);
        console.log('STEP 2: audio captured');
        if (componentAliveRef.current) setActiveStep(0); // Audio captured
        await new Promise((r) => setTimeout(r, 150));

        // STEP 3: Starting Audio Preprocessing & Signal Conditioning
        console.log('STEP 3: starting audio preprocessing & signal conditioning');
        if (componentAliveRef.current) setActiveStep(1); // Audio Preprocessing & Signal Conditioning
        await new Promise((r) => setTimeout(r, 200));

        // STEP 4: Signal Conditioning Complete
        console.log('STEP 4: audio preprocessing & signal conditioning complete');
        if (componentAliveRef.current) setActiveStep(2); // Frequency analysis / Feature extraction
        await new Promise((r) => setTimeout(r, 150));

        // STEP 5: Starting API Request
        console.log('STEP 5: starting API request (Request ID:', requestIdRef.current, ')');
        console.log('API URL:', `${API_URL}/api/analyze`);
        if (componentAliveRef.current) setActiveStep(3); // ML Analysis

        const formData = new FormData();
        formData.append('audio', rawFile, rawFile.name || 'recording.wav');
        formData.append('machine_id', machineId);
        formData.append('source', location.state?.source || 'uploaded');
        formData.append('request_id', requestIdRef.current);

        const t_start_fetch = performance.now();
        const response = await fetch(`${API_URL}/api/analyze`, {
          method: 'POST',
          body: formData,
          signal: controller.signal
        });
        const t_end_fetch = performance.now();

        clearTimeout(timeoutId);
        console.log('Response status:', response.status);
        console.log(`HTTP Request duration: ${(t_end_fetch - t_start_fetch).toFixed(2)} ms`);

        if (!response.ok) {
          let detailMsg = `Server returned status ${response.status}.`;
          try {
            const errJson = await response.json();
            if (errJson.detail) {
              detailMsg = errJson.detail;
            }
          } catch (e) {
            // Keep default status message
          }
          throw new Error(detailMsg);
        }

        // STEP 6: API Response Received
        const resultData = await response.json();
        console.log('STEP 6: API response received', resultData);

        if (componentAliveRef.current) setActiveStep(4); // AI Anomaly Detection Completed
        await new Promise((r) => setTimeout(r, 150));

        // Clear active memory store upon success
        clearActiveAudioFile();

        if (componentAliveRef.current) {
          navigate('/results', {
            state: {
              analysisData: resultData,
              machineId
            }
          });
        }
      } catch (err) {
        if (!componentAliveRef.current) return;
        clearTimeout(timeoutId);

        console.error('Frontend Processing Failure:', err);
        let userFriendlyMsg = err.message || 'An unexpected error occurred during audio processing.';
        if (err.name === 'AbortError') {
          userFriendlyMsg = 'Analysis request timed out after 25 seconds. Please check backend status and retry.';
        } else if (err.message === 'Failed to fetch' || err.name === 'TypeError') {
          userFriendlyMsg = `Unable to connect to FastAPI backend at ${API_URL}. Please ensure the backend server is running.`;
        }

        setErrorMessage(userFriendlyMsg);
      }
    };

    executeAnalysis();

    return () => {
      componentAliveRef.current = false;
      clearTimeout(timeoutId);
    };
  }, [rawFile, machineId, navigate, retryTrigger]);

  const handleRetry = () => {
    hasDispatchedRef.current = false;
    requestIdRef.current = `req_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
    setRetryTrigger((prev) => prev + 1);
  };

  return (
    <div className="bg-background text-on-surface font-body-md min-h-screen flex flex-col overflow-hidden relative pt-16 pb-24 md:pb-8 selection:bg-primary-container selection:text-on-primary-container">
      <TopNavigation />

      {/* WebGL Ambient Background */}
      <AmbientShader />

      {/* Main Container */}
      <main className="flex-grow relative w-full h-full flex flex-col items-center justify-center py-8 z-10">
        <div className="relative z-20 w-full max-w-5xl px-margin-mobile md:px-margin-desktop flex flex-col md:flex-row gap-panel-gap">
          {/* Main Visualizer Panel */}
          <div className="flex-1 tech-border bg-surface-container rounded-lg p-8 flex flex-col items-center justify-center min-h-[380px] relative overflow-hidden scanning-effect shadow-md">
            {errorMessage ? (
              <div className="text-center p-6 space-y-4">
                <div className="w-16 h-16 rounded bg-error-container/20 border border-error/40 flex items-center justify-center mx-auto text-error">
                  <span className="material-symbols-outlined text-3xl">error</span>
                </div>
                <h2 className="font-headline-md text-headline-md text-error font-bold">Acoustic Analysis Error</h2>
                <p className="font-body-md text-on-surface-variant text-sm max-w-md mx-auto leading-relaxed">
                  {errorMessage}
                </p>
                <div className="flex items-center justify-center gap-3 mt-4">
                  <button
                    onClick={handleRetry}
                    className="px-6 py-3 rounded bg-primary-container text-on-primary-container font-body-md text-body-md font-bold soft-cyan-glow hover:bg-primary-fixed transition-all cursor-pointer flex items-center gap-2"
                  >
                    <span className="material-symbols-outlined text-lg">refresh</span>
                    Retry Pipeline
                  </button>
                  <button
                    onClick={() => {
                      clearActiveAudioFile();
                      navigate('/analyze');
                    }}
                    className="px-6 py-3 rounded bg-surface-container-high border border-outline-variant text-on-surface font-body-md text-body-md hover:bg-surface-variant transition-colors cursor-pointer"
                  >
                    Return to Upload
                  </button>
                </div>
              </div>
            ) : (
              <>
                <div className="w-36 h-36 rounded-full border border-primary-container/40 flex items-center justify-center relative mb-6">
                  <div
                    className="absolute inset-0 rounded-full border-2 border-t-primary-container border-r-transparent border-b-transparent border-l-transparent animate-spin"
                    style={{ animationDuration: '2.5s' }}
                  ></div>
                  <div
                    className="absolute inset-2 rounded-full border-2 border-b-secondary border-t-transparent border-r-transparent border-l-transparent animate-spin"
                    style={{ animationDuration: '1.8s', animationDirection: 'reverse' }}
                  ></div>
                  <span className="material-symbols-outlined text-5xl text-primary-fixed-dim soft-cyan-glow">
                    waves
                  </span>
                </div>

                <h1 className="font-headline-lg text-headline-lg text-primary-fixed-dim text-center mb-2 font-bold tracking-tight">
                  Conditioning & Analyzing Machine Sound...
                </h1>
                <p className="font-data-sm text-data-sm text-on-surface-variant text-center font-medium">
                  Running ML Anomaly Detection on <strong className="text-on-surface">{machine.id} ({machine.name})</strong>
                </p>

                {/* Spectral Waveform Bars */}
                <div className="absolute bottom-4 left-6 right-6 h-12 flex items-end gap-1.5 justify-between opacity-80">
                  {[4, 8, 14, 6, 18, 10, 5, 12, 16, 7, 20, 11, 14, 6, 18, 9, 15, 8, 10, 16].map((h, i) => (
                    <div
                      key={i}
                      className="w-1.5 bg-primary-fixed-dim rounded-t transition-all duration-200 animate-pulse"
                      style={{
                        height: `${h * 2.2}px`,
                        animationDelay: `${i * 0.1}s`
                      }}
                    />
                  ))}
                </div>
              </>
            )}
          </div>

          {/* Progress Checklist Sidebar */}
          {!errorMessage && (
            <div className="w-full md:w-80 tech-border bg-surface-container rounded-lg p-6 flex flex-col justify-between">
              <div>
                <div className="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-widest mb-6 border-b border-outline-variant pb-2 flex justify-between items-center font-bold">
                  <span>ANALYSIS PIPELINE</span>
                  <span className="font-data-sm text-data-sm text-secondary font-bold">
                    {Math.min(100, Math.round(((activeStep + 1) / 5) * 100))}%
                  </span>
                </div>

                <ul className="space-y-5">
                  {[
                    'Audio captured',
                    'Audio Preprocessing & Signal Conditioning',
                    'Frequency STFT decomposition',
                    'Acoustic feature extraction',
                    'AI machine anomaly detection'
                  ].map((stepLabel, idx) => {
                    const isDone = idx < activeStep;
                    const isCurrent = idx === activeStep;

                    return (
                      <li key={idx} className="flex items-center gap-3.5">
                        {isDone ? (
                          <div className="w-6 h-6 rounded bg-secondary-container/20 border border-secondary/40 flex items-center justify-center text-secondary">
                            <span className="material-symbols-outlined text-[16px]">check</span>
                          </div>
                        ) : isCurrent ? (
                          <div className="w-6 h-6 rounded bg-primary-container/20 border border-primary-container flex items-center justify-center soft-cyan-glow">
                            <span className="w-2 h-2 rounded-full bg-primary-container pulse-dot"></span>
                          </div>
                        ) : (
                          <div className="w-6 h-6 rounded border border-outline-variant flex items-center justify-center text-outline-variant">
                            <span className="material-symbols-outlined text-[14px]">schedule</span>
                          </div>
                        )}

                        <span
                          className={`font-body-md text-sm ${
                            isDone
                              ? 'text-on-surface opacity-80'
                              : isCurrent
                              ? 'text-primary-fixed-dim font-bold'
                              : 'text-on-surface-variant/60'
                          }`}
                        >
                          {stepLabel}
                        </span>
                      </li>
                    );
                  })}
                </ul>
              </div>

              <div className="mt-8 pt-4 border-t border-outline-variant/40 font-data-sm text-data-sm text-on-surface-variant text-xs">
                Request ID: <span className="text-primary font-bold">{requestIdRef.current}</span>
              </div>
            </div>
          )}
        </div>
      </main>

      <BottomNavigation />
    </div>
  );
}

