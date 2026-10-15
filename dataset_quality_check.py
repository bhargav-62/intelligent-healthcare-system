
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "Cleaned_Dataset.csv"

print("=" * 70)
print("       MEDICARE AI - DATASET QUALITY CHECK")
print("=" * 70)

if not DATASET_PATH.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATASET_PATH}"
    )

df = pd.read_csv(DATASET_PATH)

# 1. Dataset overview
print("\n[1] DATASET OVERVIEW")
print("Shape:", df.shape)
print("Columns:", df.columns.tolist())
print("Exact duplicate rows:", int(df.duplicated().sum()))
print("Missing values:", int(df.isna().sum().sum()))

# 2. Target distribution
print("\n[2] TARGET DISTRIBUTIONS")

for col in ["disease", "outcome_variable", "risk_level"]:
    if col in df.columns:
        print(f"\n{col}:")
        print(df[col].value_counts(dropna=False).to_string())
        print("\nPercentages:")
        print(
            (df[col].value_counts(normalize=True, dropna=False) * 100)
            .round(2)
            .to_string()
        )

# 3. Feature value distributions
print("\n[3] FEATURE VALUE CHECKS")

for col in [
    "fever",
    "cough",
    "fatigue",
    "difficulty_breathing",
    "gender",
    "age",
    "blood_pressure",
    "cholesterol_level",
]:
    if col in df.columns:
        print(f"\n{col}:")
        print(df[col].value_counts(dropna=False).head(15).to_string())

# 4. Check relationships between labels
print("\n[4] LABEL RELATIONSHIPS")

if {"disease", "outcome_variable"}.issubset(df.columns):
    print("\nDisease vs outcome_variable:")
    print(pd.crosstab(df["disease"], df["outcome_variable"]))

if {"disease", "risk_level"}.issubset(df.columns):
    print("\nDisease vs risk_level:")
    print(pd.crosstab(df["disease"], df["risk_level"]))

# 5. Check scaled features
print("\n[5] SCALED FEATURE CHECK")

for col in ["age_scaled", "bp_scaled", "chol_scaled"]:
    if col in df.columns:
        print(f"\n{col}:")
        print(df[col].describe().round(3).to_string())

# 6. Identify exact duplicate examples
print("\n[6] DUPLICATE EXAMPLES")

duplicates = df[df.duplicated(keep=False)]

if duplicates.empty:
    print("No exact duplicate rows.")
else:
    print("Rows involved in exact duplicates:", len(duplicates))
    print(duplicates.head(10).to_string(index=False))

# 7. Preliminary suitability report
print("\n[7] PRELIMINARY REVIEW")

print(
    "This dataset has", len(df), "rows and",
    len(df.columns), "columns."
)

print(
    "Duplicate rows:", int(df.duplicated().sum())
)

print(
    "Disease classes:",
    df["disease"].nunique() if "disease" in df else "Unknown"
)

print("\nIMPORTANT:")
print("- This script does not modify the dataset.")
print("- Label meaning and data provenance must be verified.")
print("- No clinical accuracy is inferred from these checks.")

print("\nDATASET QUALITY CHECK COMPLETED.")
