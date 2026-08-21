// Memory store for active DOM File objects during navigation
let currentAudioFile = null;

export const setActiveAudioFile = (file) => {
  currentAudioFile = file;
};

export const getActiveAudioFile = () => {
  return currentAudioFile;
};

export const clearActiveAudioFile = () => {
  currentAudioFile = null;
};
