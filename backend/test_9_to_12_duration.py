import numpy as np
import soundfile as sf
from pathlib import Path
from app.services.audio_processor import process_audio_signal

def run_range_verification():
    sr = 16000
    test_dir = Path("test_range_temp")
    test_dir.mkdir(exist_ok=True)

    pump_file = Path("D:/pump/abnormal/00000000.wav")
    if pump_file.exists():
        y_mach, _ = sf.read(str(pump_file), dtype='float32')
        if y_mach.ndim > 1: y_mach = np.mean(y_mach, axis=1)
    else:
        t = np.linspace(0, 15.0, int(sr * 15.0), endpoint=False)
        y_mach = (0.3 * np.sin(2 * np.pi * 450 * t)).astype(np.float32)

    # Generate 5 test WAV files with exact durations
    durations = [8.9, 9.0, 10.0, 12.0, 12.1]
    file_map = []

    for d in durations:
        f_path = test_dir / f"test_{d}s.wav"
        num_samples = int(sr * d)
        if len(y_mach) >= num_samples:
            segment = y_mach[:num_samples]
        else:
            repeats = int(np.ceil(num_samples / len(y_mach)))
            segment = np.tile(y_mach, repeats)[:num_samples]
        sf.write(str(f_path), segment, sr)
        file_map.append((f"{d} sec Audio", f_path, d))

    print("\n" + "=" * 120)
    print(f"{'VERIFICATION TEST':<25} | {'DUR (s)':<8} | {'RAW RMS':<8} | {'RAW PEAK':<8} | {'VALID SIGNAL':<12} | {'GATE REASON / OUTCOME'}")
    print("=" * 120)

    for label, path_obj, target_dur in file_map:
        res_dict, _, _ = process_audio_signal(str(path_obj))
        sig = res_dict.get("signal", {})
        dur = res_dict.get("audio", {}).get("duration", 0.0)
        valid_signal = sig.get("valid_machine_signal", False)
        reason = sig.get("machine_presence_reason", "")

        status = "ACCEPTED (Proceeds to ML)" if valid_signal else "REJECTED (NO_MACHINE_SOUND)"

        print(f"{label:<25} | {dur:<8.2f} | {sig.get('rms', 0.0):<8.5f} | {sig.get('peak_amplitude', 0.0):<8.4f} | {str(valid_signal):<12} | {reason}")

    print("=" * 120 + "\n")

    # Cleanup
    for _, p, _ in file_map:
        if p.exists(): p.unlink()
    if test_dir.exists(): test_dir.rmdir()

if __name__ == "__main__":
    run_range_verification()
