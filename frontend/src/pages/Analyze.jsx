import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import TopNavigation from '../components/layout/TopNavigation';
import BottomNavigation from '../components/layout/BottomNavigation';
import AudioUploader from '../components/audio/AudioUploader';
import { machinesData } from '../data/mockData';
import { setActiveAudioFile } from '../utils/audioStore';
import { convertBlobToWavFile } from '../utils/wavEncoder';

export default function Analyze() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const initialMachineId = searchParams.get('machine') || 'id_00';

  const [selectedMachine, setSelectedMachine] = useState(
    machinesData.find((m) => m.id === initialMachineId) || machinesData[0]
  );
  const [activeTab, setActiveTab] = useState('record'); // 'record' | 'upload'

  // Recording State Machine: 'idle' | 'recording' | 'ready' | 'converting'
  const [recordingState, setRecordingState] = useState('idle');
  const [recordingTime, setRecordingTime] = useState(0);
  const [recordedWavFile, setRecordedWavFile] = useState(null);
  const [recordedAudioUrl, setRecordedAudioUrl] = useState(null);
  const [micError, setMicError] = useState('');

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);
  const streamRef = useRef(null);

  // Clean up object URL and stream on unmount
  useEffect(() => {
    return () => {
      if (recordedAudioUrl) {
        URL.revokeObjectURL(recordedAudioUrl);
      }
      stopStream();
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [recordedAudioUrl]);

  const stopStream = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
  };

  const formatTimer = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const startRecording = async () => {
    setMicError('');
    audioChunksRef.current = [];

    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Microphone API is not supported in this browser environment.');
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          autoGainControl: false,
          noiseSuppression: false,
          echoCancellation: false
        }
      });
      streamRef.current = stream;

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        stopStream();
        if (timerRef.current) clearInterval(timerRef.current);

        const rawBlob = new Blob(audioChunksRef.current, { type: mediaRecorder.mimeType || 'audio/webm' });
        
        if (rawBlob.size === 0) {
          setMicError('Recorded audio is empty. Please try recording again.');
          setRecordingState('idle');
          return;
        }

        setRecordingState('converting');

        try {
          // Convert browser mic stream into standard 16-bit PCM WAV File
          const wavFile = await convertBlobToWavFile(rawBlob, `${selectedMachine.id}_recording.wav`);
          const audioUrl = URL.createObjectURL(wavFile);

          setRecordedWavFile(wavFile);
          setRecordedAudioUrl(audioUrl);
          setRecordingState('ready');
        } catch (err) {
          console.error("WAV Encoding error:", err);
          setMicError('Unable to encode recorded audio into WAV format. Please retry.');
          setRecordingState('idle');
        }
      };

      mediaRecorder.start(100);
      setRecordingState('recording');
      setRecordingTime(0);

      timerRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } catch (err) {
      console.error("Microphone permission error:", err);
      let msg = 'Microphone permission denied or not available. Please allow microphone access or upload a WAV file.';
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        msg = 'Microphone access was denied by user or browser. Please enable microphone permissions.';
      }
      setMicError(msg);
      setRecordingState('idle');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
  };

  const handleResetRecording = () => {
    if (recordedAudioUrl) {
      URL.revokeObjectURL(recordedAudioUrl);
    }
    setRecordedWavFile(null);
    setRecordedAudioUrl(null);
    setRecordingState('idle');
    setRecordingTime(0);
    setMicError('');
  };

  const handleAnalyzeRecordedWav = () => {
    if (!recordedWavFile) return;

    setActiveAudioFile(recordedWavFile);

    navigate('/processing', {
      state: {
        source: 'rec',
        machineId: selectedMachine.id,
        rawFile: recordedWavFile
      }
    });
  };

  const handleUploadedAudioAnalyze = (fileInfo) => {
    navigate('/processing', {
      state: {
        source: 'uploaded',
        machineId: selectedMachine.id,
        rawFile: fileInfo.rawFile,
        fileInfo
      }
    });
  };

  return (
    <div className="bg-background text-on-background min-h-screen flex flex-col font-body-md selection:bg-primary-container selection:text-on-primary-container">
      <TopNavigation />

      <main className="flex-1 px-margin-mobile md:px-margin-desktop py-panel-gap mb-24 md:mb-8 flex flex-col gap-panel-gap max-w-7xl mx-auto w-full mt-16">
        {/* Header Section */}
        <section className="flex flex-col gap-unit">
          <h1 className="font-headline-lg text-headline-lg text-on-surface tracking-tight font-bold">
            Acoustic Analysis
          </h1>
          <p className="font-body-md text-body-md text-on-surface-variant">
            Capture or upload machine operating sound for acoustic condition analysis.
          </p>
        </section>

        {/* Target Machine Selector Card */}
        <section className="bg-surface-container border border-outline-variant rounded-lg p-6 flex flex-col gap-4">
          <div className="flex justify-between items-center border-b border-outline-variant pb-2">
            <span className="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-widest font-bold">
              Target Asset
            </span>
            <span className="w-2 h-2 rounded-full bg-secondary"></span>
          </div>

          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex-1 relative">
              <select
                value={selectedMachine.id}
                onChange={(e) => {
                  const m = machinesData.find((item) => item.id === e.target.value);
                  if (m) setSelectedMachine(m);
                }}
                className="w-full bg-surface text-on-surface border border-outline-variant rounded p-3 font-data-lg text-data-lg appearance-none focus:outline-none focus:border-primary-fixed-dim focus:ring-1 focus:ring-primary-fixed-dim transition-all cursor-pointer font-bold"
              >
                {machinesData.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.id} — {m.name.toUpperCase()} ({m.type})
                  </option>
                ))}
              </select>
              <span className="material-symbols-outlined absolute right-3 top-3 text-on-surface-variant pointer-events-none">
                arrow_drop_down
              </span>
            </div>

            <div className="flex flex-wrap gap-x-8 gap-y-2 font-data-sm text-data-sm text-on-surface-variant">
              <div className="flex flex-col">
                <span className="text-on-surface-variant uppercase text-[10px] font-bold">Type</span>
                <span className="text-on-surface font-semibold">{selectedMachine.type}</span>
              </div>
              <div className="flex flex-col">
                <span className="text-on-surface-variant uppercase text-[10px] font-bold">Last Analysis</span>
                <span className="text-on-surface font-semibold">{selectedMachine.lastAnalyzed || '2023-10-24 14:32'}</span>
              </div>
              <div className="flex flex-col">
                <span className="text-on-surface-variant uppercase text-[10px] font-bold">Health</span>
                <span className="text-secondary font-bold">{selectedMachine.healthScore || 98}% OPTIMAL</span>
              </div>
            </div>
          </div>
        </section>

        {/* Audio Input Area */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-panel-gap">
          {/* Input Controls Panel */}
          <div className="lg:col-span-1 bg-surface-container border border-outline-variant rounded-lg flex flex-col">
            {/* Mode Switcher Tabs */}
            <div className="flex border-b border-outline-variant">
              <button
                onClick={() => setActiveTab('record')}
                className={`flex-1 py-3 text-center font-label-caps text-label-caps cursor-pointer ${
                  activeTab === 'record'
                    ? 'text-on-surface border-b-2 border-primary-container bg-surface-variant/30 font-bold'
                    : 'text-on-surface-variant hover:bg-surface-variant/20 transition-colors'
                }`}
              >
                Record Audio
              </button>
              <button
                onClick={() => setActiveTab('upload')}
                className={`flex-1 py-3 text-center font-label-caps text-label-caps cursor-pointer ${
                  activeTab === 'upload'
                    ? 'text-on-surface border-b-2 border-primary-container bg-surface-variant/30 font-bold'
                    : 'text-on-surface-variant hover:bg-surface-variant/20 transition-colors'
                }`}
              >
                Upload Audio
              </button>
            </div>

            {/* Record Mode Content */}
            {activeTab === 'record' ? (
              <div className="flex-1 flex flex-col items-center justify-center p-6 gap-5 min-h-[340px]">
                {/* IDLE STATE */}
                {recordingState === 'idle' && (
                  <>
                    <div className="font-data-lg text-data-lg text-on-surface font-bold tracking-widest">
                      00:00:00
                    </div>

                    <button
                      onClick={startRecording}
                      className="w-24 h-24 rounded-full bg-surface-container-high border-2 border-primary-container flex items-center justify-center hover:scale-105 transition-all group relative cursor-pointer soft-cyan-glow"
                    >
                      <div className="absolute inset-0 rounded-full border border-primary-container/30 pulse-ring"></div>
                      <span className="material-symbols-outlined text-4xl text-primary-container icon-fill">
                        mic
                      </span>
                    </button>

                    <span className="font-body-sm text-body-sm text-on-surface font-bold">
                      Tap microphone to record audio
                    </span>
                  </>
                )}

                {/* RECORDING STATE */}
                {recordingState === 'recording' && (
                  <>
                    <div className="font-data-lg text-data-lg text-error font-bold tracking-widest flex items-center gap-2 animate-pulse">
                      <span className="w-3 h-3 rounded-full bg-error"></span>
                      {formatTimer(recordingTime)}
                    </div>

                    <button
                      onClick={stopRecording}
                      className="w-24 h-24 rounded-full bg-error/20 border-2 border-error flex items-center justify-center hover:scale-105 transition-all cursor-pointer shadow-lg"
                    >
                      <span className="material-symbols-outlined text-4xl text-error">
                        stop
                      </span>
                    </button>

                    <span className="font-body-sm text-body-sm text-error font-bold animate-pulse">
                      Recording sound... Tap stop when done
                    </span>
                  </>
                )}

                {/* CONVERTING STATE */}
                {recordingState === 'converting' && (
                  <div className="flex flex-col items-center justify-center gap-3">
                    <span className="material-symbols-outlined text-4xl text-primary-container animate-spin">
                      sync
                    </span>
                    <span className="font-body-md font-bold text-on-surface">
                      Encoding recorded PCM to WAV...
                    </span>
                  </div>
                )}

                {/* READY STATE */}
                {recordingState === 'ready' && (
                  <div className="w-full flex flex-col items-center gap-4">
                    <div className="flex items-center gap-2 text-secondary font-bold font-data-sm text-data-sm">
                      <span className="material-symbols-outlined text-lg">check_circle</span>
                      WAV Recording Ready ({formatTimer(recordingTime)})
                    </div>

                    {recordedAudioUrl && (
                      <audio src={recordedAudioUrl} controls className="w-full max-w-xs" />
                    )}

                    <div className="flex gap-2 w-full">
                      <button
                        onClick={handleResetRecording}
                        className="flex-1 py-2 px-3 bg-surface-container-high border border-outline-variant text-on-surface font-body-sm rounded hover:bg-surface-variant transition-colors cursor-pointer text-xs font-bold"
                      >
                        Re-record
                      </button>

                      <button
                        onClick={handleAnalyzeRecordedWav}
                        className="flex-1 py-2 px-3 bg-primary-container text-on-primary-container font-body-sm rounded soft-cyan-glow hover:bg-primary-fixed transition-all cursor-pointer text-xs font-bold flex items-center justify-center gap-1"
                      >
                        Analyze WAV
                        <span className="material-symbols-outlined text-sm">arrow_forward</span>
                      </button>
                    </div>
                  </div>
                )}

                {/* Error Message */}
                {micError && (
                  <div className="p-3 rounded bg-error-container/20 border-l-4 border-l-error text-error text-xs font-medium w-full text-center">
                    {micError}
                  </div>
                )}
              </div>
            ) : (
              <div className="p-6">
                <AudioUploader onAnalyzeFile={handleUploadedAudioAnalyze} />
              </div>
            )}
          </div>

          {/* Waveform / Visualizer Panel */}
          <div className="lg:col-span-2 bg-surface-container border border-outline-variant rounded-lg p-4 flex flex-col relative overflow-hidden">
            <div className="flex justify-between items-center mb-4 z-10">
              <span className="font-label-caps text-label-caps text-on-surface-variant font-bold">
                Live Acoustic Stream
              </span>
              <span className="font-data-sm text-data-sm text-on-surface font-bold">
                16 kHz | 16-bit PCM WAV
              </span>
            </div>

            <div className="flex-1 technical-grid rounded border border-outline-variant relative flex items-center justify-center min-h-[220px]">
              <div className="absolute inset-0 w-full h-full flex flex-col items-center justify-center gap-2">
                <span className="font-data-sm text-data-sm text-on-surface font-bold tracking-widest">
                  {recordingState === 'recording' ? 'CAPTURING MICROPHONE SIGNAL...' : 'AWAITING INPUT SIGNAL'}
                </span>
                <span className="font-data-sm text-[11px] text-on-surface-variant font-medium">
                  Press Record or Upload WAV to start inference
                </span>
              </div>
              <div className="absolute w-full h-px bg-outline-variant/60 top-1/2"></div>
            </div>
          </div>
        </section>
      </main>

      <BottomNavigation />
    </div>
  );
}
