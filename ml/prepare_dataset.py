import os
import sys
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split

# Ensure ml package is in python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.config import DATASET_DIR, DATA_DIR, RANDOM_SEED, TRAIN_RATIO, VAL_RATIO, TEST_RATIO
from ml.dataset import discover_mimii_dataset
from ml.preprocessing import load_and_preprocess_audio
from ml.features import extract_acoustic_features


def main():
    print("=" * 60)
    print("MachineSense MIMII Pump Dataset Inspection & Preparation")
    print("=" * 60)
    print(f"Target Dataset Path: {DATASET_DIR}")
    print()

    # Step 1: Discover & Inspect Dataset
    print("[STEP 1/5] Discovering & Inspecting MIMII audio recordings...")
    records, stats = discover_mimii_dataset(DATASET_DIR)

    total_files = stats.get("total_files", 0)
    if total_files == 0:
        print("ERROR: No valid WAV recordings were found in dataset directory!")
        sys.exit(1)

    print(f" -> Found {total_files} total valid WAV recordings.")
    print(f" -> Normal recordings:   {stats['normal_count']}")
    print(f" -> Abnormal recordings: {stats['abnormal_count']}")
    print()

    # Step 2: Print Dataset Statistics Breakdown
    print("[STEP 2/5] Dataset Statistics Breakdown:")
    print("-" * 60)
    print(f"Duration Stats (seconds) -> Min: {stats['duration_stats']['min']}s | Avg: {stats['duration_stats']['avg']}s | Max: {stats['duration_stats']['max']}s")
    print(f"Sample Rates Distribution -> {stats['sample_rates']}")
    print()
    print("Recordings Per Machine ID:")
    for m_id, m_data in stats["machine_stats"].items():
        print(f"  * {m_id:10s} -> Total: {m_data['total']:5d} | Normal: {m_data['normal']:5d} | Abnormal: {m_data['abnormal']:5d}")
    print()

    # Problematic Files Audit
    prob = stats["problematic_files"]
    print("Problematic Files Audit:")
    print(f"  * Corrupted files: {len(prob['corrupted'])}")
    print(f"  * Empty files:     {len(prob['empty'])}")
    print(f"  * Unsupported:     {len(prob['unsupported'])}")
    print(f"  * Duplicates:      {len(prob['duplicates'])}")
    if prob['corrupted']:
        for item in prob['corrupted']:
            print(f"    - {item}")
    print()

    # Step 3: Save Full Metadata CSV
    print("[STEP 3/5] Generating metadata CSV...")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    metadata_df = pd.DataFrame(records)
    
    metadata_path = DATA_DIR / "metadata.csv"
    metadata_df.to_csv(metadata_path, index=False)
    print(f" -> Created full metadata file: {metadata_path} ({len(metadata_df)} rows)")
    print()

    # Step 4: Reproducible Train/Val/Test Split (Preventing Data Leakage)
    print("[STEP 4/5] Creating Stratified Train/Val/Test Splits (Seed: 42)...")
    
    # Create stratify key combining machine_id and label for balanced representation
    metadata_df["stratify_key"] = metadata_df["machine_id"] + "_" + metadata_df["label"].astype(str)

    # First split: Train (70%) vs Temp (30%)
    train_df, temp_df = train_test_split(
        metadata_df,
        test_size=(VAL_RATIO + TEST_RATIO),
        random_state=RANDOM_SEED,
        stratify=metadata_df["stratify_key"]
    )

    # Second split: Validation (15%) vs Test (15%)
    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,  # 50% of 30% = 15%
        random_state=RANDOM_SEED,
        stratify=temp_df["stratify_key"]
    )

    # Drop temporary stratify_key
    cols = ["file_path", "machine_id", "label", "label_name", "duration", "sample_rate", "number_of_samples"]
    train_df = train_df[cols]
    val_df = val_df[cols]
    test_df = test_df[cols]

    train_path = DATA_DIR / "train.csv"
    val_path = DATA_DIR / "validation.csv"
    test_path = DATA_DIR / "test.csv"

    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    test_df.to_csv(test_path, index=False)

    print(f" -> Train Split:      {len(train_df)} recordings ({len(train_df)/len(metadata_df)*100:.1f}%) -> {train_path}")
    print(f" -> Validation Split: {len(val_df)} recordings ({len(val_df)/len(metadata_df)*100:.1f}%) -> {val_path}")
    print(f" -> Test Split:       {len(test_df)} recordings ({len(test_df)/len(metadata_df)*100:.1f}%) -> {test_path}")
    print()

    # Step 5: Verify Feature Extraction on Sample Audio Recordings
    print("[STEP 5/5] Verifying Acoustic Feature Extraction on Sample Audio...")
    sample_file = metadata_df.iloc[0]["file_path"]
    sample_m_id = metadata_df.iloc[0]["machine_id"]
    sample_label = metadata_df.iloc[0]["label_name"]

    print(f" -> Loading sample file: {sample_file} ({sample_m_id} - {sample_label})")
    y_norm, sr = load_and_preprocess_audio(sample_file)
    feats = extract_acoustic_features(y_norm, sr)

    print(" -> Feature Extraction Results:")
    print(f"    * Sample Rate:               {sr} Hz")
    print(f"    * RMS Energy:                {feats['rms']}")
    print(f"    * Dominant Frequency:        {feats['dominant_frequency_hz']} Hz")
    print(f"    * Spectral Centroid:         {feats['spectral_centroid_hz']} Hz")
    print(f"    * Spectral Bandwidth:        {feats['spectral_bandwidth_hz']} Hz")
    print(f"    * Spectral Rolloff:          {feats['spectral_rolloff_hz']} Hz")
    print(f"    * Spectral Flatness:         {feats['spectral_flatness']}")
    print(f"    * Zero Crossing Rate:        {feats['zero_crossing_rate']}")
    print(f"    * MFCC Shape (n_mfcc=13):    Mean count={len(feats['mfcc_mean'])}, Std count={len(feats['mfcc_std'])}")
    print()

    print("=" * 60)
    print("Dataset Inspection & Preparation Successfully Completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
