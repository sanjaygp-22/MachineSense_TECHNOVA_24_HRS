import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useTheme } from '../../context/ThemeContext';

export default function TopNavigation() {
  const navigate = useNavigate();
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-margin-mobile md:px-margin-desktop h-16 bg-surface border-b border-outline-variant text-on-surface transition-colors duration-200">
      {/* Brand Emblem */}
      <div
        className="flex items-center gap-3 cursor-pointer group"
        onClick={() => navigate('/dashboard')}
      >
        <div className="w-8 h-8 rounded bg-primary-container/20 border border-primary-container/40 flex items-center justify-center text-primary-container soft-cyan-glow group-hover:scale-105 transition-all">
          <span className="material-symbols-outlined icon-fill text-xl">sensors</span>
        </div>
        <div className="flex flex-col">
          <span className="font-headline-md text-headline-md font-bold tracking-tight text-on-surface">
            MachineSense
          </span>
          <span className="font-label-caps text-[9px] text-on-surface-variant uppercase tracking-widest -mt-1 hidden sm:inline">
            Acoustic Intelligence Station
          </span>
        </div>
      </div>

      {/* Desktop Navigation */}
      <nav className="hidden md:flex items-center gap-1">
        <NavLink
          to="/dashboard"
          className={({ isActive }) =>
            `flex items-center gap-2 px-3 py-1.5 rounded font-label-caps text-label-caps uppercase transition-all ${
              isActive
                ? 'text-on-surface bg-surface-container-high border-b-2 border-primary-container font-bold'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low'
            }`
          }
        >
          <span className="material-symbols-outlined text-[18px]">dashboard</span>
          Overview
        </NavLink>

        <NavLink
          to="/machines"
          className={({ isActive }) =>
            `flex items-center gap-2 px-3 py-1.5 rounded font-label-caps text-label-caps uppercase transition-all ${
              isActive
                ? 'text-on-surface bg-surface-container-high border-b-2 border-primary-container font-bold'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low'
            }`
          }
        >
          <span className="material-symbols-outlined text-[18px]">precision_manufacturing</span>
          Machines
        </NavLink>

        <NavLink
          to="/analyze"
          className={({ isActive }) =>
            `flex items-center gap-2 px-3 py-1.5 rounded font-label-caps text-label-caps uppercase transition-all ${
              isActive
                ? 'text-on-surface bg-surface-container-high border-b-2 border-primary-container font-bold'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low'
            }`
          }
        >
          <span className="material-symbols-outlined text-[18px] icon-fill">analytics</span>
          Analyze
        </NavLink>

        <NavLink
          to="/history"
          className={({ isActive }) =>
            `flex items-center gap-2 px-3 py-1.5 rounded font-label-caps text-label-caps uppercase transition-all ${
              isActive
                ? 'text-on-surface bg-surface-container-high border-b-2 border-primary-container font-bold'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low'
            }`
          }
        >
          <span className="material-symbols-outlined text-[18px]">history</span>
          History
        </NavLink>

        <NavLink
          to="/frequency"
          className={({ isActive }) =>
            `flex items-center gap-2 px-3 py-1.5 rounded font-label-caps text-label-caps uppercase transition-all ${
              isActive
                ? 'text-on-surface bg-surface-container-high border-b-2 border-primary-container font-bold'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low'
            }`
          }
        >
          <span className="material-symbols-outlined text-[18px]">equalizer</span>
          Spectrum
        </NavLink>

        <NavLink
          to="/settings"
          className={({ isActive }) =>
            `flex items-center gap-2 px-3 py-1.5 rounded font-label-caps text-label-caps uppercase transition-all ${
              isActive
                ? 'text-on-surface bg-surface-container-high border-b-2 border-primary-container font-bold'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low'
            }`
          }
        >
          <span className="material-symbols-outlined text-[18px]">settings</span>
          Settings
        </NavLink>
      </nav>

      {/* Right Header Status & Theme Toggle */}
      <div className="flex items-center gap-3">
        {/* Theme Toggle Button */}
        <button
          onClick={toggleTheme}
          aria-label="Toggle Theme"
          title={`Switch to ${theme === 'light' ? 'Dark' : 'Light'} Mode`}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded border border-outline-variant bg-surface-container-low text-on-surface hover:bg-surface-container-high transition-all cursor-pointer font-label-caps text-label-caps uppercase"
        >
          <span className="material-symbols-outlined text-[18px]">
            {theme === 'light' ? 'dark_mode' : 'light_mode'}
          </span>
          <span className="hidden sm:inline font-bold">{theme === 'light' ? 'Dark' : 'Light'}</span>
        </button>

        <div className="hidden lg:flex items-center gap-2 bg-surface-container-low border border-outline-variant px-3 py-1.5 rounded text-xs font-data-sm text-secondary">
          <span className="w-2 h-2 rounded-full bg-secondary pulse-dot"></span>
          <span>SYSTEM ONLINE</span>
        </div>

        <button
          onClick={() => navigate('/analyze')}
          className="bg-primary-container text-on-primary-container font-label-caps text-label-caps px-4 py-2 rounded soft-cyan-glow hover:bg-primary-fixed transition-all cursor-pointer font-bold flex items-center gap-1.5"
        >
          <span className="material-symbols-outlined text-[16px]">graphic_eq</span>
          ANALYZE
        </button>
      </div>
    </header>
  );
}
