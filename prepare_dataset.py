
from pathlib import Path
import json
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
SOURCE = BASE_DIR / "Cleaned_Dataset.csv"
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

if not SOURCE.exists():
    raise FileNotFoundError(f"Missing source dataset: {SOURCE}")

# Preserve the original dataset by reading it without modification.
df = pd.read_csv(SOURCE)

print("=" * 60)
print("MEDICARE AI - EXPLORATORY DATA PREPARATION")
print("=" * 60)

print("Original shape:", df.shape)

# Save an untouched copy for traceability.
raw_copy = RAW_DIR / "original_dataset.csv"
df.to_csv(raw_copy, index=False)

# Create a separate exploratory version.
exploratory = df.drop_duplicates().copy()

# Existing scaled columns have unknown preprocessing history.
# Exclude them from this exploratory version until verified.
scaled_columns = [
    "age_scaled",
    "bp_scaled",
    "chol_scaled",
]

removed_scaled = [
    col for col in scaled_columns
    if col in exploratory.columns
]

exploratory = exploratory.drop(
    columns=removed_scaled,
    errors="ignore"
)

# Save prepared data separately.
output_path = (
    PROCESSED_DIR / "exploratory_dataset.csv"
)
exploratory.to_csv(output_path, index=False)

# Record exactly what happened.
report = {
    "source_file": str(SOURCE.name),
    "original_rows": int(len(df)),
    "original_columns": int(len(df.columns)),
    "exact_duplicate_rows_removed": int(
        df.duplicated().sum()
    ),
    "exploratory_rows": int(len(exploratory)),
    "exploratory_columns": int(len(exploratory.columns)),
    "removed_scaled_columns": removed_scaled,
    "missing_values_remaining": int(
        exploratory.isna().sum().sum()
    ),
    "purpose": (
        "Exploratory analysis only; not approved "
        "for disease model training."
    ),
}

report_path = PROCESSED_DIR / "preparation_report.json"

with open(report_path, "w", encoding="utf-8") as file:
    json.dump(report, file, indent=4)

print("\nOriginal dataset preserved:", raw_copy)
print("Exploratory dataset saved:", output_path)
print("Preparation report saved:", report_path)
print("\nPreparation summary:")
print(json.dumps(report, indent=4))

print("\nIMPORTANT:")
print("This dataset is not clinically validated.")
print("Do not use it to generate diagnoses or prescriptions.")
print("Verify the data source before training a model.")
print("\nSTEP 3 COMPLETED.")
