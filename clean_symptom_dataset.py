
from pathlib import Path
import json
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

train_path = RAW_DIR / "Training.csv"
test_path = RAW_DIR / "Testing.csv"

train = pd.read_csv(train_path)
test = pd.read_csv(test_path)

# Remove completely empty columns, such as Unnamed: 133
train = train.dropna(axis=1, how="all")
test = test.dropna(axis=1, how="all")

target = "prognosis"

if target not in train.columns or target not in test.columns:
    raise ValueError("The prognosis column is missing.")

feature_columns = [c for c in train.columns if c != target]

if set(feature_columns) != set(
    c for c in test.columns if c != target
):
    raise ValueError("Training and testing features do not match.")

if train[feature_columns + [target]].isna().any().any():
    raise ValueError("Training data contains missing values.")

if test[feature_columns + [target]].isna().any().any():
    raise ValueError("Testing data contains missing values.")

# Confirm that the features are binary symptom indicators
for col in feature_columns:
    values = set(train[col].unique())
    if not values.issubset({0, 1}):
        raise ValueError(
            f"Unexpected values in symptom column {col}: {values}"
        )

# Check whether identical symptom patterns have conflicting labels
label_counts = train.groupby(feature_columns)[target].nunique()
conflicting_patterns = int((label_counts > 1).sum())

# Remove exact duplicates only; preserve the original file
clean = train.drop_duplicates().reset_index(drop=True)

# Save the exploratory unique-row dataset
output_path = PROCESSED_DIR / "unique_symptom_patterns.csv"
clean.to_csv(output_path, index=False)

report = {
    "original_training_rows": int(len(train)),
    "unique_complete_rows": int(len(clean)),
    "exact_duplicate_rows_removed": int(len(train) - len(clean)),
    "symptom_feature_count": int(len(feature_columns)),
    "disease_class_count": int(train[target].nunique()),
    "conflicting_symptom_patterns": conflicting_patterns,
    "testing_rows": int(len(test)),
    "training_and_testing_overlap_warning": (
        "The supplied test set shares symptom patterns with training."
    ),
    "purpose": (
        "Exploratory analysis only; not clinically validated "
        "and not suitable for clinical diagnosis."
    ),
}

report_path = PROCESSED_DIR / "symptom_dataset_report.json"
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("=== DATA PREPARATION COMPLETE ===")
print(json.dumps(report, indent=2))
print(f"\nCleaned dataset: {output_path}")
print(f"Report: {report_path}")
