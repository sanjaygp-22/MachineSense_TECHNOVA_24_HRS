import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

import Dashboard from './pages/Dashboard';
import Machines from './pages/Machines';
import MachineHealth from './pages/MachineHealth';
import Analyze from './pages/Analyze';
import Processing from './pages/Processing';
import Results from './pages/Results';
import FrequencyAnalysis from './pages/FrequencyAnalysis';
import History from './pages/History';
import Settings from './pages/Settings';
import ResearchInsights from './pages/ResearchInsights';

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/machines" element={<Machines />} />
        <Route path="/health" element={<MachineHealth />} />
        <Route path="/analyze" element={<Analyze />} />
        <Route path="/processing" element={<Processing />} />
        <Route path="/results" element={<Results />} />
        <Route path="/frequency" element={<FrequencyAnalysis />} />
        <Route path="/history" element={<History />} />
        <Route path="/research" element={<ResearchInsights />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Router>
  );
}

