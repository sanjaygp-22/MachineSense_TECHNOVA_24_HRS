import os
from pathlib import Path
import soundfile as sf
import numpy as np

def benchmark_dataset_and_silence():
    pump_dir = Path("D:/pump")
    if not pump_dir.exists():
        print(f"Directory {pump_dir} does not exist.")
        return

    wav_files = list(pump_dir.rglob("*.wav"))
    print(f"Total MIMII Pump WAV files found in D:/pump: {len(wav_files)}")

    results = []

    # Measure MIMII dataset files (Normal & Abnormal)
    for p in wav_files[:30]:  # Sample 30 dataset files across normal/abnormal
        try:
            y, sr = sf.read(str(p), dtype='float32')
            if y.ndim > 1:
                y = np.mean(y, axis=1)
            raw_peak = float(np.max(np.abs(y)))
            raw_rms = float(np.sqrt(np.mean(y ** 2)))
            duration = float(len(y) / sr)
            is_abnormal = "abnormal" in str(p).lower()
            cat = "Machine (Abnormal)" if is_abnormal else "Machine (Normal)"
            results.append((cat, p.name, raw_rms, raw_peak, duration, True))
        except Exception as e:
            pass

    # Measure Quiet Room & Digital Silence
    sr = 16000
    # 1. Digital Silence
    silence_y = np.zeros(sr * 3, dtype=np.float32)
    results.append(("Digital Silence", "digital_silence.wav", float(np.sqrt(np.mean(silence_y**2))), float(np.max(np.abs(silence_y))), 3.0, False))

    # 2. Quiet Room Mic Log (Measured from live browser user recording id_00_recording.wav)
    results.append(("Quiet Room (Mic Recorded)", "id_00_recording.wav", 0.028298, 1.000000, 6.06, False))

    # 3. Quiet Room Mic Log (Measured with AGC disabled)
    results.append(("Quiet Room (AGC Disabled)", "id_00_no_agc.wav", 0.011732, 1.000000, 5.82, False))

    print("\n" + "=" * 100)
    print(f"{'CATEGORY':<28} | {'FILENAME':<24} | {'RAW RMS':<10} | {'RAW PEAK':<10} | {'DUR':<5} | {'CURRENT':<7} | {'PROPOSED':<7} | {'REACH RF?'}")
    print("=" * 100)

    machine_rms_list = []
    quiet_rms_list = []

    for cat, name, raw_rms, raw_peak, dur, should_rf in results:
        curr_gate = "PASS" if (raw_rms >= 0.002 and raw_peak >= 0.008 and dur >= 0.5) else "REJECT"
        prop_gate = "PASS" if (raw_rms >= 0.035 and raw_peak >= 0.015 and dur >= 0.5) else "REJECT"

        if should_rf:
            machine_rms_list.append(raw_rms)
        else:
            quiet_rms_list.append(raw_rms)

        print(f"{cat:<28} | {name[:22]:<24} | {raw_rms:<10.6f} | {raw_peak:<10.6f} | {dur:<5.1f} | {curr_gate:<7} | {prop_gate:<7} | {'YES' if should_rf else 'NO'}")

    print("=" * 100)
    if machine_rms_list:
        print(f"\n[SUMMARY STATS]")
        print(f"  Minimum Genuine Machine RAW RMS: {min(machine_rms_list):.6f}")
        print(f"  Maximum Genuine Machine RAW RMS: {max(machine_rms_list):.6f}")
        print(f"  Average Genuine Machine RAW RMS: {sum(machine_rms_list)/len(machine_rms_list):.6f}")
    if quiet_rms_list:
        print(f"  Maximum Quiet Room / Silence RAW RMS: {max(quiet_rms_list):.6f}")

if __name__ == "__main__":
    benchmark_dataset_and_silence()
