import React from 'react';

export default function AudioFileCard({ fileInfo, onRemove, onAnalyze, isProcessing }) {
  if (!fileInfo) return null;

  const { name, format, sizeFormatted, durationFormatted, audioUrl } = fileInfo;

  return (
    <div className="tech-border bg-surface-container rounded-lg p-6 flex flex-col gap-4 relative overflow-hidden shadow-sm">
      <div className="flex items-start justify-between gap-4 border-b border-outline-variant pb-4">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="w-12 h-12 rounded bg-primary-container/20 border border-primary-container/40 flex items-center justify-center flex-shrink-0 text-primary-fixed-dim soft-cyan-glow">
            <span className="material-symbols-outlined text-2xl icon-fill">
              graphic_eq
            </span>
          </div>
          <div className="truncate">
            <h4 className="font-headline-md text-body-lg text-on-surface truncate font-bold">
              {name}
            </h4>
            <p className="font-data-sm text-data-sm text-on-surface-variant text-xs mt-0.5 font-semibold">
              {format.toUpperCase()} • {sizeFormatted} • {durationFormatted}
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={onRemove}
          className="text-on-surface-variant hover:text-error hover:bg-error-container/20 p-2 rounded transition-colors flex items-center gap-1 text-xs font-label-caps cursor-pointer"
          title="Remove selected audio file"
        >
          <span className="material-symbols-outlined text-base">delete</span>
          <span className="hidden sm:inline">Remove</span>
        </button>
      </div>

      {/* Audio Player */}
      <div className="mt-2">
        <audio
          src={audioUrl}
          controls
          className="w-full rounded bg-surface-container-low accent-primary-container h-10 border border-outline-variant/30"
        />
      </div>

      {/* Primary Action Button */}
      <button
        type="button"
        onClick={onAnalyze}
        disabled={isProcessing}
        className="w-full mt-2 bg-primary-container text-on-primary-container font-body-md text-body-md font-bold py-3.5 rounded soft-cyan-glow hover:bg-primary-fixed transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        <span className="material-symbols-outlined text-xl">analytics</span>
        {isProcessing ? 'Conditioning Signal & Analyzing...' : 'Run Machine ML Anomaly Diagnostic'}
      </button>
    </div>
  );
}

