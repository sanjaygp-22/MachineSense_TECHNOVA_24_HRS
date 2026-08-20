import numpy as np
import soundfile as sf
from pathlib import Path
from app.services.audio_processor import process_audio_signal, check_machine_audio

def run_tests():
    sr = 16000
    test_dir = Path("test_8s_temp")
    test_dir.mkdir(exist_ok=True)

    # 1. 3.0s audio
    file_3s = test_dir / "audio_3s.wav"
    sf.write(str(file_3s), np.zeros(int(sr * 3.0), dtype=np.float32), sr)

    # 2. 7.9s audio
    file_7_9s = test_dir / "audio_7_9s.wav"
    sf.write(str(file_7_9s), np.random.normal(0, 0.028, int(sr * 7.9)).astype(np.float32), sr)

    # 3. 8.0s machine audio (truncated MIMII pump file 00000000.wav)
    pump_file = Path("D:/pump/abnormal/00000000.wav")
    file_8_0s = test_dir / "machine_8_0s.wav"
    if pump_file.exists():
        y_mach, _ = sf.read(str(pump_file), dtype='float32')
        if y_mach.ndim > 1: y_mach = np.mean(y_mach, axis=1)
        sf.write(str(file_8_0s), y_mach[:int(sr * 8.0)], sr)
    else:
        t = np.linspace(0, 8.0, int(sr * 8.0), endpoint=False)
        m_wave = (0.3 * np.sin(2 * np.pi * 450 * t)).astype(np.float32)
        sf.write(str(file_8_0s), m_wave, sr)

    test_cases = [
        ("VERIFICATION 1 (3.0s Audio)", file_3s),
        ("VERIFICATION 2 (7.9s Audio)", file_7_9s),
        ("VERIFICATION 3 (8.0s Machine Audio)", file_8_0s),
        ("VERIFICATION 4 (10.0s Genuine Machine)", pump_file if pump_file.exists() else file_8_0s),
    ]

    print("\n" + "=" * 120)
    print(f"{'VERIFICATION TEST':<36} | {'DUR (s)':<8} | {'RAW RMS':<8} | {'RAW PEAK':<8} | {'VALID SIGNAL':<12} | {'GATE REASON / MESSAGE'}")
    print("=" * 120)

    for label, path_obj in test_cases:
        res_dict, _, _ = process_audio_signal(str(path_obj))
        sig = res_dict.get("signal", {})
        dur = res_dict.get("audio", {}).get("duration", 0.0)
        valid_signal = sig.get("valid_machine_signal", False)
        reason = sig.get("machine_presence_reason", "")

        print(f"{label:<36} | {dur:<8.2f} | {sig.get('rms', 0.0):<8.5f} | {sig.get('peak_amplitude', 0.0):<8.4f} | {str(valid_signal):<12} | {reason}")

    print("=" * 120 + "\n")

    # Cleanup
    for p in [file_3s, file_7_9s, file_8_0s]:
        if p.exists(): p.unlink()
    if test_dir.exists(): test_dir.rmdir()

if __name__ == "__main__":
    run_tests()
