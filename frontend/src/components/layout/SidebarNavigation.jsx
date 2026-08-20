import React from 'react';
import { NavLink } from 'react-router-dom';
import { useTheme } from '../../context/ThemeContext';

export default function SidebarNavigation() {
  const { theme, toggleTheme } = useTheme();

  return (
    <aside className="hidden md:flex flex-col py-margin-mobile gap-unit bg-surface-container-low border-r border-outline-variant h-screen w-80 shrink-0 sticky top-0 z-40 text-on-surface font-body-md transition-colors duration-200">
      <div className="px-6 pb-6 border-b border-outline-variant mb-4 flex justify-between items-center">
        <h1 className="font-headline-md text-headline-md font-bold text-on-surface tracking-tight">
          MachineSense
        </h1>
        <button
          onClick={toggleTheme}
          aria-label="Toggle Theme"
          title={`Switch to ${theme === 'light' ? 'Dark' : 'Light'} Mode`}
          className="p-2 rounded-full hover:bg-surface-variant transition-colors cursor-pointer text-on-surface"
        >
          <span className="material-symbols-outlined text-xl">
            {theme === 'light' ? 'dark_mode' : 'light_mode'}
          </span>
        </button>
      </div>

      <nav className="flex-1 px-4 overflow-y-auto space-y-1">
        <NavLink
          to="/dashboard"
          className={({ isActive }) =>
            `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors font-body-md ${
              isActive
                ? 'bg-primary-container text-on-primary-container font-semibold soft-cyan-glow'
                : 'text-on-surface-variant hover:bg-surface-variant hover:text-on-surface'
            }`
          }
        >
          <span className="material-symbols-outlined">dashboard</span>
          <span>Overview</span>
        </NavLink>

        <NavLink
          to="/machines"
          className={({ isActive }) =>
            `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors font-body-md ${
              isActive
                ? 'bg-primary-container text-on-primary-container font-semibold soft-cyan-glow'
                : 'text-on-surface-variant hover:bg-surface-variant hover:text-on-surface'
            }`
          }
        >
          <span className="material-symbols-outlined">precision_manufacturing</span>
          <span>Machines</span>
        </NavLink>

        <NavLink
          to="/analyze"
          className={({ isActive }) =>
            `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors font-body-md ${
              isActive
                ? 'bg-primary-container text-on-primary-container font-semibold soft-cyan-glow'
                : 'text-on-surface-variant hover:bg-surface-variant hover:text-on-surface'
            }`
          }
        >
          <span className="material-symbols-outlined">analytics</span>
          <span>Analyze</span>
        </NavLink>

        <NavLink
          to="/history"
          className={({ isActive }) =>
            `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors font-body-md ${
              isActive
                ? 'bg-primary-container text-on-primary-container font-semibold soft-cyan-glow'
                : 'text-on-surface-variant hover:bg-surface-variant hover:text-on-surface'
            }`
          }
        >
          <span className="material-symbols-outlined">history</span>
          <span>History</span>
        </NavLink>

        <NavLink
          to="/research"
          className={({ isActive }) =>
            `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors font-body-md ${
              isActive
                ? 'bg-primary-container text-on-primary-container font-semibold soft-cyan-glow'
                : 'text-on-surface-variant hover:bg-surface-variant hover:text-on-surface'
            }`
          }
        >
          <span className="material-symbols-outlined">biotech</span>
          <span>Research Insights</span>
        </NavLink>

        <NavLink
          to="/frequency"
          className={({ isActive }) =>
            `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors font-body-md ${
              isActive
                ? 'bg-primary-container text-on-primary-container font-semibold soft-cyan-glow'
                : 'text-on-surface-variant hover:bg-surface-variant hover:text-on-surface'
            }`
          }
        >
          <span className="material-symbols-outlined">equalizer</span>
          <span>Frequency Spectrum</span>
        </NavLink>

        <NavLink
          to="/settings"
          className={({ isActive }) =>
            `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors font-body-md ${
              isActive
                ? 'bg-primary-container text-on-primary-container font-semibold soft-cyan-glow'
                : 'text-on-surface-variant hover:bg-surface-variant hover:text-on-surface'
            }`
          }
        >
          <span className="material-symbols-outlined">settings</span>
          <span>Settings</span>
        </NavLink>
      </nav>

      {/* Footer Theme Bar */}
      <div className="p-4 border-t border-outline-variant">
        <button
          onClick={toggleTheme}
          className="w-full flex items-center justify-between px-3 py-2 rounded-lg bg-surface-container border border-outline-variant hover:bg-surface-variant transition-colors cursor-pointer text-on-surface"
        >
          <span className="font-label-caps text-label-caps uppercase font-bold flex items-center gap-2">
            <span className="material-symbols-outlined text-[18px]">palette</span>
            Theme: {theme.toUpperCase()}
          </span>
          <span className="material-symbols-outlined text-lg">
            {theme === 'light' ? 'dark_mode' : 'light_mode'}
          </span>
        </button>
      </div>
    </aside>
  );
}
