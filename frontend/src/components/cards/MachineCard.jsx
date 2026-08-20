import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function MachineCard({ machine }) {
  const navigate = useNavigate();

  const getStatusBadge = (status) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
      case 'normal':
      case 'optimal':
        return {
          bg: 'bg-secondary-container/20',
          border: 'border-secondary/30',
          text: 'text-secondary',
          dot: 'bg-secondary soft-cyan-glow',
          label: 'NORMAL'
        };
      case 'warning':
      case 'degrading':
        return {
          bg: 'bg-tertiary-container/20',
          border: 'border-tertiary-fixed-dim/30',
          text: 'text-tertiary-fixed-dim',
          dot: 'bg-tertiary-fixed-dim animate-pulse',
          label: 'DEGRADING'
        };
      case 'critical':
      case 'abnormal':
        return {
          bg: 'bg-error-container/20',
          border: 'border-error/40',
          text: 'text-error',
          dot: 'bg-error animate-pulse',
          label: 'CRITICAL'
        };
      default:
        return {
          bg: 'bg-surface-variant',
          border: 'border-outline-variant',
          text: 'text-on-surface-variant',
          dot: 'bg-outline',
          label: 'UNKNOWN'
        };
    }
  };

  const badge = getStatusBadge(machine.status);

  return (
    <div className="bg-surface tech-border rounded-xl p-6 flex flex-col justify-between gap-5 relative group transition-all hover:border-outline shadow-sm">
      {/* Top Header */}
      <div className="flex justify-between items-start">
        <div className="flex flex-col gap-0.5">
          <span className="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-widest font-bold">
            {machine.id} • {machine.code || 'MIMII-ASSET'}
          </span>
          <h3 className="font-headline-md text-headline-md text-on-surface font-bold group-hover:text-primary transition-colors">
            {machine.name}
          </h3>
          <span className="font-body-sm text-body-sm text-on-surface-variant text-xs">
            {machine.type}
          </span>
        </div>

        <div className={`flex items-center gap-1.5 ${badge.bg} border ${badge.border} px-2.5 py-1 rounded font-data-sm text-data-sm text-[11px] font-bold ${badge.text}`}>
          <span className={`w-2 h-2 rounded-full ${badge.dot}`}></span>
          <span>{badge.label}</span>
        </div>
      </div>

      <div className="h-px bg-outline-variant/50 w-full"></div>

      {/* Technical Data Grid */}
      <div className="flex flex-col gap-2.5">
        <div className="flex items-center justify-between border-b border-outline-variant/30 pb-1.5">
          <span className="font-body-sm text-body-sm text-on-surface-variant">Signature</span>
          <span className="font-data-sm text-data-sm text-primary font-bold">
            {machine.dominantFreq || '450 Hz'} | 16kHz
          </span>
        </div>
        <div className="flex items-center justify-between border-b border-outline-variant/30 pb-1.5">
          <span className="font-body-sm text-body-sm text-on-surface-variant">Location</span>
          <span className="font-data-sm text-data-sm text-on-surface font-semibold">{machine.location}</span>
        </div>
        <div className="flex items-center justify-between border-b border-outline-variant/30 pb-1.5">
          <span className="font-body-sm text-body-sm text-on-surface-variant">Health Rating</span>
          <span className={`font-data-sm text-data-sm font-bold ${badge.text}`}>
            {machine.healthScore}% OPTIMAL
          </span>
        </div>
      </div>

      {/* Sparkline Visualization */}
      <div className="w-full h-8 bg-surface-container-low border border-outline-variant/40 rounded px-2 flex items-center justify-end overflow-hidden">
        <svg className={`w-full h-full stroke-current ${badge.text} fill-none`} preserveAspectRatio="none" viewBox="0 0 100 20">
          <path
            d={
              machine.status === 'Critical'
                ? 'M0,10 L15,18 L30,2 L45,18 L60,1 L75,19 L100,10'
                : machine.status === 'Warning'
                ? 'M0,10 L20,15 L40,5 L60,16 L80,4 L100,10'
                : 'M0,10 L20,12 L40,8 L60,13 L80,7 L100,10'
            }
            strokeWidth="1.5"
            vectorEffect="non-scaling-stroke"
          ></path>
        </svg>
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-2 gap-2 mt-1">
        <button
          onClick={() => navigate(`/health?id=${machine.id}`)}
          className="bg-surface-container-high border border-outline-variant text-on-surface font-body-sm text-body-sm py-2 rounded hover:bg-surface-variant transition-colors cursor-pointer text-xs font-semibold"
        >
          Details
        </button>
        <button
          onClick={() => navigate(`/analyze?machine=${machine.id}`)}
          className="bg-primary-container text-on-primary-container font-body-sm text-body-sm py-2 rounded soft-cyan-glow hover:bg-primary-fixed transition-all cursor-pointer text-xs font-bold flex items-center justify-center gap-1"
        >
          Analyze
          <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
        </button>
      </div>
    </div>
  );
}

