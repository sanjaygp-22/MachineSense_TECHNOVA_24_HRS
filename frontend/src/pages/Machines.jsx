import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import TopNavigation from '../components/layout/TopNavigation';
import BottomNavigation from '../components/layout/BottomNavigation';
import MachineCard from '../components/cards/MachineCard';
import { machinesData } from '../data/mockData';

export default function Machines() {
  const [filter, setFilter] = useState('All');
  const [search, setSearch] = useState('');
  const navigate = useNavigate();

  const filteredMachines = machinesData.filter((m) => {
    const matchesFilter =
      filter === 'All' ||
      (filter === 'Healthy' && (m.status === 'Healthy' || m.status === 'Normal')) ||
      (filter === 'Warning' && (m.status === 'Warning' || m.status === 'Degrading')) ||
      (filter === 'Critical' && (m.status === 'Critical' || m.status === 'Abnormal'));

    const matchesSearch =
      m.name.toLowerCase().includes(search.toLowerCase()) ||
      m.id.toLowerCase().includes(search.toLowerCase()) ||
      m.code.toLowerCase().includes(search.toLowerCase()) ||
      m.location.toLowerCase().includes(search.toLowerCase());

    return matchesFilter && matchesSearch;
  });

  return (
    <div className="bg-background text-on-surface font-body-md min-h-screen pb-24 md:pb-8 pt-16 selection:bg-primary-container selection:text-on-primary-container">
      <TopNavigation />

      <main className="max-w-7xl mx-auto px-margin-mobile md:px-margin-desktop py-panel-gap flex flex-col gap-panel-gap w-full">
        {/* Controls Header Row */}
        <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
          <div>
            <h1 className="font-headline-lg text-headline-lg text-on-surface">Machine Inventory</h1>
            <p className="font-body-md text-body-md text-on-surface-variant mt-1">
              Monitoring {machinesData.length} active acoustic assets across industrial sectors.
            </p>
          </div>

          <div className="flex gap-3 w-full sm:w-auto items-center">
            {/* Search Field */}
            <div className="relative flex-1 sm:w-64">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none text-[20px]">
                search
              </span>
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full bg-surface-container-low border border-outline-variant text-on-surface font-body-sm text-body-sm rounded py-2 pl-10 pr-4 focus:outline-none focus:border-primary-container focus:ring-1 focus:ring-primary-container transition-colors placeholder:text-outline"
                placeholder="Search ID, Name, Sector..."
                type="text"
              />
            </div>
          </div>
        </div>

        {/* Filter Chips */}
        <div className="flex gap-2 border-b border-outline-variant pb-3 overflow-x-auto">
          {['All', 'Healthy', 'Warning', 'Critical'].map((f) => {
            const isActive = filter === f;
            return (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-4 py-1.5 rounded font-label-caps text-label-caps uppercase transition-all flex items-center gap-2 cursor-pointer ${
                  isActive
                    ? 'bg-primary-container text-on-primary-container font-bold soft-cyan-glow'
                    : 'bg-surface-container border border-outline-variant text-on-surface-variant hover:text-on-surface'
                }`}
              >
                {f === 'Healthy' && <span className="w-2 h-2 rounded-full bg-secondary"></span>}
                {f === 'Warning' && <span className="w-2 h-2 rounded-full bg-tertiary-fixed-dim"></span>}
                {f === 'Critical' && <span className="w-2 h-2 rounded-full bg-error"></span>}
                {f === 'All' ? 'All Assets' : f}
              </button>
            );
          })}
        </div>

        {/* Inventory Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-panel-gap">
          {filteredMachines.map((m) => (
            <MachineCard key={m.id} machine={m} />
          ))}
        </div>
      </main>

      {/* Floating Action Button for Analysis */}
      <button
        onClick={() => navigate('/analyze')}
        className="fixed bottom-20 md:bottom-8 right-6 w-14 h-14 bg-primary-container text-on-primary-container rounded-full soft-cyan-glow flex items-center justify-center hover:scale-105 transition-transform z-40 cursor-pointer font-bold"
        title="Analyze Machine Acoustic"
      >
        <span className="material-symbols-outlined text-[28px] icon-fill">mic</span>
      </button>

      <BottomNavigation />
    </div>
  );
}

