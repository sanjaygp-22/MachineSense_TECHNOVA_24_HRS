/**
 * Converts any audio Blob (WebM, OGG, M4A) recorded by browser MediaRecorder
 * into a standard 16-bit PCM WAV File object suitable for machine analysis.
 */
export async function convertBlobToWavFile(blob, filename = 'recording.wav', targetSampleRate = 16000) {
  const arrayBuffer = await blob.arrayBuffer();
  
  // Use AudioContext to decode browser recording
  const audioContext = new (window.AudioContext || window.webkitAudioContext)();
  const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
  
  // Convert stereo to mono by averaging channels
  const numChannels = 1;
  const length = Math.floor(audioBuffer.duration * targetSampleRate);
  const offlineCtx = new OfflineAudioContext(numChannels, length, targetSampleRate);
  
  const source = offlineCtx.createBufferSource();
  source.buffer = audioBuffer;
  source.connect(offlineCtx.destination);
  source.start(0);
  
  const renderedBuffer = await offlineCtx.startRendering();
  const pcmData = renderedBuffer.getChannelData(0);

  // Calculate browser-side diagnostic metrics on raw PCM array
  let minSample = 1.0;
  let maxSample = -1.0;
  let sumSq = 0;
  let nearZeroCount = 0;

  for (let i = 0; i < pcmData.length; i++) {
    const val = pcmData[i];
    if (val < minSample) minSample = val;
    if (val > maxSample) maxSample = val;
    sumSq += val * val;
    if (Math.abs(val) < 0.001) nearZeroCount++;
  }

  const rms = Math.sqrt(sumSq / (pcmData.length || 1));
  const nearZeroPct = ((nearZeroCount / (pcmData.length || 1)) * 100).toFixed(2);

  console.log("=== BROWSER PCM DIAGNOSTIC METRICS ===");
  console.log("Sample Rate:", targetSampleRate, "Hz");
  console.log("Channels:", numChannels);
  console.log("Number of Samples:", pcmData.length);
  console.log("Duration:", audioBuffer.duration.toFixed(2), "s");
  console.log("Min Sample:", minSample.toFixed(6));
  console.log("Max Sample:", maxSample.toFixed(6));
  console.log("Browser RMS:", rms.toFixed(6));
  console.log(`Near-Zero Samples (<0.001): ${nearZeroCount} (${nearZeroPct}%)`);
  console.log("======================================");
  
  // Create 16-bit PCM WAV File
  const wavBuffer = createWavBuffer(pcmData, targetSampleRate);
  const wavBlob = new Blob([wavBuffer], { type: 'audio/wav' });
  
  // Close context to free memory
  if (audioContext.state !== 'closed') {
    await audioContext.close();
  }
  
  return new File([wavBlob], filename, { type: 'audio/wav', lastModified: Date.now() });
}

function createWavBuffer(samples, sampleRate) {
  const buffer = new ArrayBuffer(44 + samples.length * 2);
  const view = new DataView(buffer);

  /* RIFF identifier */
  writeString(view, 0, 'RIFF');
  /* RIFF chunk length */
  view.setUint32(4, 36 + samples.length * 2, true);
  /* RIFF type */
  writeString(view, 8, 'WAVE');
  /* format chunk identifier */
  writeString(view, 12, 'fmt ');
  /* format chunk length */
  view.setUint32(16, 16, true);
  /* sample format (raw PCM = 1) */
  view.setUint16(20, 1, true);
  /* channel count (1 = mono) */
  view.setUint16(22, 1, true);
  /* sample rate */
  view.setUint32(24, sampleRate, true);
  /* byte rate (sampleRate * blockAlign) */
  view.setUint32(28, sampleRate * 2, true);
  /* block align (channel count * bytes per sample) */
  view.setUint16(32, 2, true);
  /* bits per sample (16 bit) */
  view.setUint16(34, 16, true);
  /* data chunk identifier */
  writeString(view, 36, 'data');
  /* data chunk length */
  view.setUint32(40, samples.length * 2, true);

  /* Write 16-bit PCM samples */
  let offset = 44;
  for (let i = 0; i < samples.length; i++, offset += 2) {
    const s = Math.max(-1, Math.min(1, samples[i]));
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
  }

  return buffer;
}

function writeString(view, offset, string) {
  for (let i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i));
  }
}
