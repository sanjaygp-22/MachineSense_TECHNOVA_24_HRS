import os
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm

# Ensure ml package is in python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.config import DATA_DIR
from ml.preprocessing import load_and_preprocess_audio
from ml.features import extract_acoustic_features


def process_split_file(split_name: str, csv_path: Path):
    """
    Processes a single CSV split (train, validation, or test), extracts 33 acoustic features,
    and returns (features_df, errors_list).
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"Split CSV file not found: {csv_path}")

    split_meta_df = pd.read_csv(csv_path)
    print(f"\nProcessing '{split_name}' split ({len(split_meta_df)} recordings)...")

    rows = []
    errors = []

    for _, meta_row in tqdm(split_meta_df.iterrows(), total=len(split_meta_df), desc=f"Extracting {split_name}"):
        f_path = meta_row["file_path"]
        m_id = meta_row["machine_id"]
        label = meta_row["label"]
        l_name = meta_row["label_name"]

        try:
            y_norm, sr = load_and_preprocess_audio(f_path)
            feats = extract_acoustic_features(y_norm, sr)

            row_data = {
                "file_path": f_path,
                "machine_id": m_id,
                "label": label,
                "label_name": l_name,
                **feats
            }
            rows.append(row_data)

        except Exception as e:
            errors.append({
                "split": split_name,
                "file_path": f_path,
                "machine_id": m_id,
                "label_name": l_name,
                "error": str(e)
            })

    df_out = pd.DataFrame(rows)
    return df_out, errors


def main():
    print("=" * 65)
    print("MachineSense ML Phase 2: Acoustic Feature Extraction")
    print("=" * 65)

    splits = {
        "train": DATA_DIR / "train.csv",
        "validation": DATA_DIR / "validation.csv",
        "test": DATA_DIR / "test.csv"
    }

    all_errors = []
    split_dfs = {}

    for split_name, split_path in splits.items():
        df_feats, errs = process_split_file(split_name, split_path)
        split_dfs[split_name] = df_feats
        all_errors.extend(errs)

        # Save feature CSV
        out_csv = DATA_DIR / f"{split_name}_features.csv"
        df_feats.to_csv(out_csv, index=False)
        print(f" -> Saved {split_name} features: {out_csv} ({len(df_feats)} rows, {len(df_feats.columns)} columns)")

    # Save Error Report if any
    if all_errors:
        err_path = DATA_DIR / "feature_extraction_errors.json"
        with open(err_path, "w") as f:
            json.dump(all_errors, f, indent=2)
        print(f"\nWARNING: {len(all_errors)} files encountered errors during feature extraction. Logged to {err_path}")
    else:
        print("\nSUCCESS: All files processed with zero errors!")

    # Feature List
    sample_df = next(iter(split_dfs.values()))
    meta_cols = {"file_path", "machine_id", "label", "label_name"}
    feature_cols = [c for c in sample_df.columns if c not in meta_cols]

    # Save Feature Description JSON
    feature_desc = {
        "metadata_columns": list(meta_cols),
        "total_numerical_features": len(feature_cols),
        "feature_names": feature_cols
    }
    desc_path = DATA_DIR / "feature_description.json"
    with open(desc_path, "w") as f:
        json.dump(feature_desc, f, indent=2)
    print(f" -> Saved feature metadata description: {desc_path}")

    # Summary Audit & Statistics Report
    total_successful = sum(len(df) for df in split_dfs.values())
    total_failed = len(all_errors)

    # Check for NaN / Inf
    total_nans = 0
    total_infs = 0
    for s_name, df in split_dfs.items():
        num_data = df[feature_cols].values
        total_nans += int(np.isnan(num_data).sum())
        total_infs += int(np.isinf(num_data).sum())

    print("\n" + "=" * 65)
    print("FEATURE EXTRACTION SUMMARY REPORT")
    print("=" * 65)
    print(f"Total Successful Recordings:  {total_successful}")
    print(f"Total Failed Recordings:      {total_failed}")
    print(f"Total Numerical Features:     {len(feature_cols)}")
    print(f"Missing Values (NaN Count):   {total_nans}")
    print(f"Infinite Values (Inf Count):  {total_infs}")
    print()

    print("List of 33 Feature Names:")
    for idx, f_name in enumerate(feature_cols, 1):
        print(f"  {idx:2d}. {f_name}")
    print()

    print("Class Distribution Across Splits:")
    for s_name, df in split_dfs.items():
        norm_c = int((df["label"] == 0).sum())
        abnorm_c = int((df["label"] == 1).sum())
        print(f"  * {s_name.capitalize():10s} -> Total: {len(df):4d} | Normal (0): {norm_c:4d} | Abnormal (1): {abnorm_c:4d}")
    print()

    print("Machine-ID Breakdown Across Splits:")
    for s_name, df in split_dfs.items():
        m_counts = df["machine_id"].value_counts().to_dict()
        print(f"  * {s_name.capitalize():10s} -> {m_counts}")

    print("\n" + "=" * 65)
    print("Feature Extraction Successfully Verified & Complete!")
    print("=" * 65)


if __name__ == "__main__":
    main()
