import numpy as np
import soundfile as sf
from pathlib import Path
from app.services.audio_processor import process_audio_signal, check_machine_audio

def test_silence_and_machine():
    test_dir = Path("test_audio_samples")
    test_dir.mkdir(exist_ok=True)

    # 1. Create pure digital silence WAV (3 seconds of zeros at 16kHz)
    silence_path = test_dir / "digital_silence.wav"
    sr = 16000
    zeros = np.zeros(sr * 3, dtype=np.float32)
    sf.write(str(silence_path), zeros, sr)

    # 2. Create quiet ambient room noise (3 seconds of low noise peak ~0.001)
    ambient_path = test_dir / "quiet_room.wav"
    quiet_noise = np.random.normal(0, 0.0005, sr * 3).astype(np.float32)
    sf.write(str(ambient_path), quiet_noise, sr)

    # Test Digital Silence
    res_silence, _, _ = process_audio_signal(str(silence_path))
    sig_silence = res_silence["signal"]
    print("\n--- TEST 1: DIGITAL SILENCE ---")
    print(f"Raw Peak: {sig_silence['peak_amplitude']}")
    print(f"Raw RMS:  {sig_silence['rms']}")
    print(f"Valid Machine Signal: {sig_silence['valid_machine_signal']}")
    print(f"Reason: {sig_silence['machine_presence_reason']}")

    # Test Quiet Ambient Room
    res_ambient, _, _ = process_audio_signal(str(ambient_path))
    sig_ambient = res_ambient["signal"]
    print("\n--- TEST 2: QUIET ROOM AMBIENT NOISE ---")
    print(f"Raw Peak: {sig_ambient['peak_amplitude']}")
    print(f"Raw RMS:  {sig_ambient['rms']}")
    print(f"Valid Machine Signal: {sig_ambient['valid_machine_signal']}")
    print(f"Reason: {sig_ambient['machine_presence_reason']}")

    # Clean up test directory
    silence_path.unlink()
    ambient_path.unlink()
    test_dir.rmdir()

if __name__ == "__main__":
    test_silence_and_machine()
