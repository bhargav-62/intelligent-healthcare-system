
from pathlib import Path
import pandas as pd

# Project folder
BASE_DIR = Path(__file__).resolve().parent

print("=" * 70)
print("          MEDICARE AI - PROJECT AUDIT")
print("=" * 70)

# --------------------------------------------------
# STEP 1: Inspect all project files
# --------------------------------------------------
print("\n[STEP 1] PROJECT FILES")

for path in sorted(BASE_DIR.rglob("*")):
    if path.is_file() and ".venv" not in path.parts:
        print(f"{path.relative_to(BASE_DIR)}")

# --------------------------------------------------
# STEP 2: Inspect all CSV datasets
# --------------------------------------------------
print("\n[STEP 2] DATASET AUDIT")

csv_files = list(BASE_DIR.rglob("*.csv"))

if not csv_files:
    print("No CSV datasets found.")
else:
    for file_path in csv_files:
        try:
            df = pd.read_csv(file_path)

            print("\n" + "-" * 60)
            print("FILE:", file_path.relative_to(BASE_DIR))
            print("-" * 60)

            print("Rows:", df.shape[0])
            print("Columns:", df.shape[1])
            print("\nColumn names:")
            print(df.columns.tolist())

            print("\nData types:")
            print(df.dtypes.to_string())

            print("\nMissing values per column:")
            print(df.isnull().sum().to_string())

            print("\nTotal missing values:",
                  int(df.isnull().sum().sum()))

            print("Duplicate rows:", int(df.duplicated().sum()))

            print("\nFirst 3 records:")
            print(df.head(3).to_string(index=False))

        except Exception as error:
            print(f"Could not read {file_path.name}: {error}")

# --------------------------------------------------
# STEP 3: Check model files
# --------------------------------------------------
print("\n[STEP 3] MODEL FILES")

model_files = [
    "best_model.pkl",
    "disease_encoder.pkl",
    "medicine_database.pkl"
]

for filename in model_files:
    file_path = BASE_DIR / filename

    if file_path.exists():
        print(f"[FOUND] {filename}")
        print(f"        Size: {file_path.stat().st_size:,} bytes")
    else:
        print(f"[MISSING] {filename}")

# --------------------------------------------------
# STEP 4: Check expected dataset dependencies
# --------------------------------------------------
print("\n[STEP 4] EXPECTED DATA FILES")

expected_files = [
    "Training.csv",
    "medicine.csv",
    "symtoms_df.csv",
    "precautions_df.csv",
    "workout_df.csv",
    "description.csv",
    "medications.csv",
    "diets.csv"
]

for filename in expected_files:
    matches = list(BASE_DIR.rglob(filename))

    if matches:
        print(f"[FOUND] {filename}")
    else:
        print(f"[NOT FOUND] {filename}")

# --------------------------------------------------
# FINAL REPORT
# --------------------------------------------------
print("\n" + "=" * 70)
print("AUDIT COMPLETED")
print("No project files were modified.")
print("=" * 70)
