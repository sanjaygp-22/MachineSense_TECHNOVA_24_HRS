import React from 'react';

export default function WaveformVisualizer({ samples = [], height = 120 }) {
  // If samples are provided (e.g. 500 normalized floats), downsample/normalize for rendering
  const dataPoints = samples.length > 0 ? samples : Array.from({ length: 100 }, (_, i) => Math.sin(i * 0.2) * 0.5);

  const totalPoints = dataPoints.length;

  // Convert normalized samples [-1.0, 1.0] into SVG Y coordinates (0 at top, 100 at bottom, mid at 50)
  const svgPoints = dataPoints.map((val, idx) => {
    const x = (idx / (totalPoints - 1 || 1)) * 100;
    const y = 50 - val * 40; // Scale amplitude to 40% height around center line
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });

  const pathD = `M ${svgPoints.join(' L ')}`;

  return (
    <div className="tech-border bg-surface-container-low rounded-lg p-4 flex flex-col gap-2 w-full relative overflow-hidden">
      <div className="flex justify-between items-center border-b border-outline-variant/30 pb-1.5">
        <span className="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider font-bold flex items-center gap-1.5">
          <span className="material-symbols-outlined text-[14px] text-primary-fixed-dim">graphic_eq</span>
          Time-Domain Acoustic Waveform
        </span>
        <span className="font-data-sm text-[10px] text-on-surface-variant font-mono">
          {totalPoints} Points • 16 kHz Mono
        </span>
      </div>

      <div className={`relative w-full h-[${height}px] flex items-center justify-center`}>
        {/* Background Grid & Midline */}
        <div className="absolute inset-0 flex flex-col justify-between pointer-events-none opacity-20">
          <div className="w-full h-px bg-outline"></div>
          <div className="w-full h-px bg-primary-container"></div>
          <div className="w-full h-px bg-outline"></div>
        </div>

        {/* SVG Waveform Line */}
        <svg className="w-full h-full" preserveAspectRatio="none" viewBox="0 0 100 100">
          <defs>
            <filter id="waveGlow">
              <feGaussianBlur result="coloredBlur" stdDeviation="1.5"></feGaussianBlur>
              <feMerge>
                <feMergeNode in="coloredBlur"></feMergeNode>
                <feMergeNode in="SourceGraphic"></feMergeNode>
              </feMerge>
            </filter>
          </defs>

          {/* Center Zero-Line */}
          <line x1="0" y1="50" x2="100" y2="50" stroke="#3b494c" strokeWidth="0.5" strokeDasharray="2,2" />

          {/* Waveform Path */}
          <path
            d={pathD}
            fill="none"
            stroke="#00e5ff"
            strokeWidth="1.2"
            filter="url(#waveGlow)"
          />
        </svg>
      </div>
    </div>
  );
}
