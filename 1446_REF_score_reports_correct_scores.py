# -*- coding: utf-8 -*-
"""
Created on Sun Nov 23 16:35:06 2025

@author: Mike Thelwall
"""
import pandas as pd
import re
import os

# === FILE NAMES (edit these as needed) ===
ref_file = "1446_REF_score_reports_correct_scores.txt"  # first file
pred_file = "second_scores_file.txt"                    # <-- change to your second file name
output_file = "score_precision_results.txt"             # output text file
main_directory = r"C:\Users\Mike Thelwall\Dropbox\papers\0 unfinished\LLM prompts for single score extraction"

os.chdir(main_directory)
# === LOAD FILES ===
# First file: must have columns "ID" and "Correct score"
df_ref = pd.read_csv(ref_file, sep="\t")

# Second file: first column is ID, remaining columns are score predictions
df_pred = pd.read_csv(pred_file, sep="\t")

# Ensure ID column exists in both and is numeric (optional but often helpful)
df_ref["ID"] = pd.to_numeric(df_ref["ID"], errors="raise")
df_pred["ID"] = pd.to_numeric(df_pred["ID"], errors="raise")

# === CLEAN PREDICTION COLUMNS ===
# Steps for every column in the second file except "ID":
# (1) trim leading/trailing spaces
# (2) remove a single '*' from the right, if present
# (3) trim any spaces from the right
# (4) convert to float; if not a plain number (digits, optional decimal, optional leading minus) -> 0

num_pattern = re.compile(r"^-?\d+(\.\d+)?$")  # digits, optional decimal, optional leading '-'

def clean_value(x):
    """Clean a single cell according to the rules and return a float."""
    if pd.isna(x):
        return 0.0

    s = str(x)

    # (1) trim leading/trailing spaces
    s = s.strip()

    # (2) remove a single '*' from the right, if there is one
    if s.endswith("*"):
        s = s[:-1]

    # (3) trim any spaces from the right
    s = s.rstrip()

    # (4) convert to float if it's just a number (with optional minus and decimal), else 0
    if num_pattern.fullmatch(s):
        return float(s)
    else:
        return 0.0

# Apply cleaning to all non-ID columns in the second file
for col in df_pred.columns:
    if col == "ID":
        continue
    df_pred[col] = df_pred[col].apply(clean_value)

# === MERGE ON ID ===
df = pd.merge(df_ref, df_pred, on="ID", how="inner")

correct_col = "Correct score"
tolerance = 0.005

# Make sure Correct score is numeric
df[correct_col] = pd.to_numeric(df[correct_col], errors="raise")

# === CALCULATE STATISTICS AND SAVE TO TEXT FILE ===
with open(output_file, "w", encoding="utf-8") as f:
    f.write(f"Reference file: {ref_file}\n")
    f.write(f"Prediction file: {pred_file}\n")
    f.write(f"Number of rows after merge: {len(df)}\n")
    f.write(f"Tolerance: ±{tolerance}\n\n")

    total_rows = len(df)

    for col in df_pred.columns:
        if col == "ID":
            continue

        y_true = df[correct_col].astype(float)
        y_pred = df[col].astype(float)

        abs_diff = (y_true - y_pred).abs()

        # --- Precision (all rows) ---
        matches_all = (abs_diff <= tolerance).sum()
        pct_all = (matches_all / total_rows * 100) if total_rows > 0 else 0.0

        # --- Precision excluding -1 predictions ---
        mask_pred_not_minus1 = (y_pred != -1)
        total_non_minus1 = mask_pred_not_minus1.sum()

        matches_non_minus1 = ((abs_diff <= tolerance) & mask_pred_not_minus1).sum()
        pct_non_minus1 = (matches_non_minus1 / total_non_minus1 * 100) if total_non_minus1 > 0 else 0.0

        f.write(f"Column: {col}\n")
        f.write(f"  Precision (all rows): {matches_all}/{total_rows} ({pct_all:.2f}%)\n")
        f.write(
            "  Precision (predictions != -1): "
            f"{matches_non_minus1}/{total_non_minus1} ({pct_non_minus1:.2f}%)\n"
        )
        f.write(f"  Count of predictions != -1: {total_non_minus1}\n\n")

print(f"Done. Results written to: {output_file}")
