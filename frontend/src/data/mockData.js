export const machinesData = [
  {
    id: "id_00",
    name: "Pump Asset (id_00)",
    code: "MIMII-00",
    type: "MIMII Industrial Pump 00",
    healthScore: 96,
    status: "Healthy",
    location: "Plant A - Deck 1",
    sector: "Pump Array 1",
    lastAnalyzed: "Just now",
    confidence: "97.3%",
    dominantFreq: "167.7 Hz",
    stability: "98%",
    noiseLevel: "Low",
    pattern: "Normal baseline hydraulic acoustics",
    recommendation: "Continue regular operation. Next scheduled acoustic inspection in 14 days.",
    icon: "water_pump",
    anomalies: 0,
    totalAnalyses: 1248,
    avgHealth: "96.2%"
  },
  {
    id: "id_02",
    name: "Pump Asset (id_02)",
    code: "MIMII-02",
    type: "MIMII Industrial Pump 02",
    healthScore: 92,
    status: "Healthy",
    location: "Plant A - Deck 2",
    sector: "Pump Array 1",
    lastAnalyzed: "10 mins ago",
    confidence: "94.2%",
    dominantFreq: "452 Hz",
    stability: "94%",
    noiseLevel: "Low",
    pattern: "Normal steady compression cycles",
    recommendation: "System operating within optimal acoustic parameters.",
    icon: "water_pump",
    anomalies: 0,
    totalAnalyses: 890,
    avgHealth: "92.4%"
  },
  {
    id: "id_04",
    name: "Pump Asset (id_04)",
    code: "MIMII-04",
    type: "MIMII Industrial Pump 04",
    healthScore: 78,
    status: "Warning",
    location: "Plant B - Lower Deck",
    sector: "Pump Array 2",
    lastAnalyzed: "45 mins ago",
    confidence: "88.5%",
    dominantFreq: "487 Hz",
    stability: "81%",
    noiseLevel: "Medium",
    pattern: "Sub-harmonic frequency fluctuations detected",
    recommendation: "Schedule bearing inspection and check impeller mounting alignment.",
    icon: "water_pump",
    anomalies: 2,
    totalAnalyses: 1042,
    avgHealth: "84.5%"
  },
  {
    id: "id_06",
    name: "Pump Asset (id_06)",
    code: "MIMII-06",
    type: "MIMII Industrial Pump 06",
    healthScore: 45,
    status: "Critical",
    location: "Plant B - Main Deck",
    sector: "Pump Array 2",
    lastAnalyzed: "2 mins ago",
    confidence: "99.1%",
    dominantFreq: "449.1 Hz",
    stability: "48%",
    noiseLevel: "High",
    pattern: "Severe acoustic anomaly & bearing cavitation distortion",
    recommendation: "Immediate inspection recommended. Check motor alignment and fluid seals.",
    icon: "warning",
    anomalies: 6,
    totalAnalyses: 1530,
    avgHealth: "54.0%"
  }
];

export const fleetHealthTrend = [
  { day: "Mon", health: 91 },
  { day: "Tue", health: 93 },
  { day: "Wed", health: 89 },
  { day: "Thu", health: 94 },
  { day: "Fri", health: 92 },
  { day: "Sat", health: 96 },
  { day: "Sun", health: 94 }
];

export const historyLogs = [
  {
    id: 1,
    machineId: "id_00",
    machineName: "Pump Asset (id_00)",
    type: "Acoustic Scan",
    time: "Today • 14:32",
    health: 96,
    status: "Healthy",
    duration: "10.0s"
  },
  {
    id: 2,
    machineId: "id_02",
    machineName: "Pump Asset (id_02)",
    type: "Acoustic Scan",
    time: "Today • 09:15",
    health: 92,
    status: "Healthy",
    duration: "10.0s"
  },
  {
    id: 3,
    machineId: "id_04",
    machineName: "Pump Asset (id_04)",
    type: "Frequency Spike Detected",
    time: "Yesterday • 18:45",
    health: 78,
    status: "Warning",
    duration: "10.0s"
  },
  {
    id: 4,
    machineId: "id_06",
    machineName: "Pump Asset (id_06)",
    type: "Abnormal Anomaly Warning",
    time: "Yesterday • 11:10",
    health: 45,
    status: "Critical",
    duration: "10.0s"
  }
];
