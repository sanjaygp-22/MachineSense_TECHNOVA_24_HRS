import React from 'react';

export default function TrendChart({ records = [], height = 180 }) {
  // Generate last 7 days (including today)
  const days = [];
  const now = new Date();
  for (let i = 6; i >= 0; i--) {
    const d = new Date(now);
    d.setDate(d.getDate() - i);
    days.push({
      dateStr: d.toISOString().substring(0, 10),
      label: d.toLocaleDateString('en-US', { weekday: 'short' })
    });
  }

  // Group real SQLite records by day
  const chartData = days.map((day, idx) => {
    const dayRecs = records.filter((r) => r.created_at && r.created_at.startsWith(day.dateStr));
    if (dayRecs.length === 0) {
      return { ...day, x: (idx / 6) * 100, y: null, score: null };
    }

    const scores = dayRecs.map((r) => {
      const lbl = (r.prediction_label || '').toLowerCase();
      if (lbl === 'normal') return Math.round((1 - (r.abnormal_probability || 0)) * 100);
      if (lbl === 'abnormal') return Math.round((1 - (r.abnormal_probability || 0.8)) * 100);
      return 100;
    });

    const avgScore = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
    // Y SVG coordinate: 100 - avgScore (0 score -> 90 y, 100 score -> 10 y)
    const yVal = Math.max(10, Math.min(90, 100 - avgScore));
    return { ...day, x: (idx / 6) * 100, y: yVal, score: avgScore };
  });

  // Filter valid data points
  const validPoints = chartData.filter((p) => p.y !== null);

  // Generate SVG path d string
  let pathD = '';
  if (validPoints.length > 0) {
    pathD = validPoints.reduce((acc, pt, i) => {
      return i === 0 ? `M ${pt.x},${pt.y}` : `${acc} L ${pt.x},${pt.y}`;
    }, '');
  }

  // Generate fill path d string
  let fillD = '';
  if (validPoints.length > 0) {
    const firstX = validPoints[0].x;
    const lastX = validPoints[validPoints.length - 1].x;
    fillD = `${pathD} L ${lastX},100 L ${firstX},100 Z`;
  }

  return (
    <div className={`relative w-full h-[${height}px] z-10 flex items-end`}>
      {/* Grid Lines */}
      <div className="absolute inset-0 flex flex-col justify-between pointer-events-none opacity-20">
        <div className="w-full h-px bg-outline"></div>
        <div className="w-full h-px bg-outline"></div>
        <div className="w-full h-px bg-outline"></div>
        <div className="w-full h-px bg-outline"></div>
      </div>

      {/* SVG Trend Line */}
      <svg className="absolute inset-0 w-full h-full" preserveAspectRatio="none" viewBox="0 0 100 100">
        <defs>
          <linearGradient id="trendGrad" x1="0%" x2="0%" y1="0%" y2="100%">
            <stop offset="0%" stopColor="#00e5ff" stopOpacity="0.4"></stop>
            <stop offset="100%" stopColor="#00e5ff" stopOpacity="0"></stop>
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur result="coloredBlur" stdDeviation="2"></feGaussianBlur>
            <feMerge>
              <feMergeNode in="coloredBlur"></feMergeNode>
              <feMergeNode in="SourceGraphic"></feMergeNode>
            </feMerge>
          </filter>
        </defs>

        {fillD && <path d={fillD} fill="url(#trendGrad)"></path>}
        {pathD && <path className="waveform-path" d={pathD} fill="none" filter="url(#glow)" stroke="#00e5ff" strokeWidth="1.8"></path>}

        {validPoints.map((pt, i) => (
          <circle key={i} cx={pt.x} cy={pt.y} fill="#0d1516" r="2.5" stroke="#00e5ff" strokeWidth="1.2"></circle>
        ))}
      </svg>

      {/* X-Axis Labels */}
      <div className="absolute bottom-0 left-0 w-full flex justify-between transform translate-y-6 px-2">
        {chartData.map((d, i) => (
          <span key={i} className={`font-data-mono text-[10px] ${d.score !== null ? 'text-secondary font-bold' : 'text-outline'}`}>
            {d.label}
          </span>
        ))}
      </div>
    </div>
  );
}
