
import pandas as pd
from pathlib import Path

p = Path("data/raw")

train = pd.read_csv(p / "Training.csv")
test = pd.read_csv(p / "Testing.csv")

# Remove completely empty columns only
train = train.dropna(axis=1, how="all")
test = test.dropna(axis=1, how="all")

target = "prognosis"
features = [c for c in train.columns if c != target]

print("=== TRAINING DATA ===")
print("Rows:", len(train))
print("Unique complete rows:", len(train.drop_duplicates()))
print("Duplicate complete rows:", train.duplicated().sum())

print("\n=== FEATURE PATTERNS ===")
unique_patterns = train[features].drop_duplicates()
print("Unique symptom patterns:", len(unique_patterns))
print("Repeated symptom patterns:", len(train) - len(unique_patterns))

pattern_labels = train.groupby(features, dropna=False)[target].nunique()
conflicting = pattern_labels[pattern_labels > 1]
print("Patterns associated with multiple diseases:", len(conflicting))

print("\n=== TEST/TRAIN OVERLAP ===")
train_patterns = set(
    map(tuple, train[features].itertuples(index=False, name=None))
)
test_patterns = set(
    map(tuple, test[features].itertuples(index=False, name=None))
)
overlap = train_patterns.intersection(test_patterns)

print("Unique test symptom patterns:", len(test_patterns))
print("Test patterns also present in training:", len(overlap))

print("\n=== CLASS DISTRIBUTION ===")
print(train[target].value_counts().describe())
print("\nAll classes:")
print(train[target].value_counts().to_string())

print("\n=== TEST FEATURE COMPATIBILITY ===")
print("Same feature names:", set(features) == set(
    c for c in test.columns if c != target
))
print("Test rows:", len(test))
print("Test disease classes:", test[target].nunique())
