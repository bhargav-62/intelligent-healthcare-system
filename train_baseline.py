
from pathlib import Path
import json

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.preprocessing import LabelEncoder
from sklearn.dummy import DummyClassifier
import joblib

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
MODEL_DIR = BASE_DIR / "models"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Load and validate the training dataset
df = pd.read_csv(RAW_DIR / "Training.csv")
df = df.dropna(axis=1, how="all")

target = "prognosis"
if target not in df.columns:
    raise ValueError("Missing target column: prognosis")

feature_columns = [c for c in df.columns if c != target]

X = df[feature_columns]
y = df[target].astype(str)

if X.isna().any().any() or y.isna().any():
    raise ValueError("Missing values found.")

# Remove repeated rows before splitting to prevent duplicates
# from appearing in both training and validation partitions.
df = df.drop_duplicates().reset_index(drop=True)
X = df[feature_columns]
y = df[target].astype(str)

print("Rows after deduplication:", len(df))
print("Unique diseases:", y.nunique())
print("Class counts:")
print(y.value_counts().to_string())

# A stratified split requires enough examples per class.
counts = y.value_counts()
if counts.min() < 2:
    raise ValueError(
        "At least two distinct rows per disease are required "
        "for a stratified split."
    )

X_train, X_val, y_train, y_val = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y,
)

# Baseline: always predict the most frequent training class.
dummy = DummyClassifier(strategy="most_frequent")
dummy.fit(X_train, y_train)
dummy_pred = dummy.predict(X_val)

# Random Forest baseline
model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1,
)
model.fit(X_train, y_train)
pred = model.predict(X_val)

print("\n=== VALIDATION RESULTS ===")
print("Dummy accuracy:", round(accuracy_score(y_val, dummy_pred), 4))
print("Random Forest accuracy:", round(accuracy_score(y_val, pred), 4))
print("Random Forest macro F1:", round(
    f1_score(y_val, pred, average="macro", zero_division=0), 4
))
print("\nClassification report:")
print(classification_report(y_val, pred, zero_division=0))

# Save the baseline model and metadata separately from old artifacts.
joblib.dump(model, MODEL_DIR / "baseline_symptom_model.joblib")

metadata = {
    "model_type": "RandomForestClassifier",
    "feature_columns": feature_columns,
    "classes": sorted(y.unique().tolist()),
    "training_rows_after_deduplication": int(len(df)),
    "validation_fraction": 0.25,
    "random_state": 42,
    "validation_accuracy": float(accuracy_score(y_val, pred)),
    "validation_macro_f1": float(
        f1_score(y_val, pred, average="macro", zero_division=0)
    ),
    "limitations": [
        "Educational dataset; not clinically validated.",
        "Deduplication leaves only a small number of distinct patterns.",
        "Validation metrics do not establish real-world diagnostic accuracy.",
        "Do not use for diagnosis, treatment, or medicine prescribing.",
    ],
}

(PROCESSED_DIR / "baseline_model_report.json").write_text(
    json.dumps(metadata, indent=2),
    encoding="utf-8",
)

print("\nModel saved:", MODEL_DIR / "baseline_symptom_model.joblib")
print("Report saved:", PROCESSED_DIR / "baseline_model_report.json")
