import React from 'react';
import { NavLink } from 'react-router-dom';

export default function BottomNavigation() {
  return (
    <nav className="md:hidden fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-4 py-2 bg-surface-container border-t border-outline-variant pb-safe">
      <NavLink
        to="/dashboard"
        className={({ isActive }) =>
          `flex flex-col items-center justify-center p-1 transition-all ${
            isActive
              ? 'text-primary-fixed-dim bg-primary-fixed-dim/10 rounded-full px-3 py-1 scale-95'
              : 'text-on-surface-variant hover:text-primary-fixed-dim'
          }`
        }
      >
        <span className="material-symbols-outlined mb-0.5">dashboard</span>
        <span className="font-label-caps text-[9px]">Overview</span>
      </NavLink>

      <NavLink
        to="/machines"
        className={({ isActive }) =>
          `flex flex-col items-center justify-center p-1 transition-all ${
            isActive
              ? 'text-primary-fixed-dim bg-primary-fixed-dim/10 rounded-full px-3 py-1 scale-95'
              : 'text-on-surface-variant hover:text-primary-fixed-dim'
          }`
        }
      >
        <span className="material-symbols-outlined mb-0.5">precision_manufacturing</span>
        <span className="font-label-caps text-[9px]">Machines</span>
      </NavLink>

      <NavLink
        to="/analyze"
        className={({ isActive }) =>
          `flex flex-col items-center justify-center p-1 transition-all ${
            isActive
              ? 'text-primary-fixed-dim bg-primary-fixed-dim/10 rounded-full px-3 py-1 scale-95 font-bold'
              : 'text-on-surface-variant hover:text-primary-fixed-dim'
          }`
        }
      >
        <span className="material-symbols-outlined mb-0.5 icon-fill">analytics</span>
        <span className="font-label-caps text-[9px]">Analyze</span>
      </NavLink>

      <NavLink
        to="/history"
        className={({ isActive }) =>
          `flex flex-col items-center justify-center p-1 transition-all ${
            isActive
              ? 'text-primary-fixed-dim bg-primary-fixed-dim/10 rounded-full px-3 py-1 scale-95'
              : 'text-on-surface-variant hover:text-primary-fixed-dim'
          }`
        }
      >
        <span className="material-symbols-outlined mb-0.5">history</span>
        <span className="font-label-caps text-[9px]">History</span>
      </NavLink>

      <NavLink
        to="/settings"
        className={({ isActive }) =>
          `flex flex-col items-center justify-center p-1 transition-all ${
            isActive
              ? 'text-primary-fixed-dim bg-primary-fixed-dim/10 rounded-full px-3 py-1 scale-95'
              : 'text-on-surface-variant hover:text-primary-fixed-dim'
          }`
        }
      >
        <span className="material-symbols-outlined mb-0.5">settings</span>
        <span className="font-label-caps text-[9px]">Settings</span>
      </NavLink>
    </nav>
  );
}

