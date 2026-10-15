
from pathlib import Path
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.metrics import make_scorer, f1_score

BASE_DIR = Path(__file__).resolve().parent
data_path = BASE_DIR / "data" / "raw" / "Training.csv"

df = pd.read_csv(data_path)
df = df.dropna(axis=1, how="all")
df = df.drop_duplicates().reset_index(drop=True)

X = df.drop(columns=["prognosis"])
y = df["prognosis"].astype(str)

counts = y.value_counts()
print("Distinct records:", len(df))
print("Disease classes:", y.nunique())
print("Smallest class:", counts.min())
print("Largest class:", counts.max())

# Five-fold validation needs at least five distinct examples
# for every class. Do not proceed if this condition fails.
if counts.min() < 5:
    raise ValueError(
        "Some classes have fewer than 5 records. "
        "Use fewer folds or obtain better data."
    )

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42,
)

models = {
    "Dummy baseline": DummyClassifier(strategy="most_frequent"),
    "Random Forest": RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
    ),
}

for name, model in models.items():
    scores = cross_validate(
        model,
        X,
        y,
        cv=cv,
        scoring={
            "accuracy": "accuracy",
            "macro_f1": make_scorer(
                f1_score,
                average="macro",
                zero_division=0,
            ),
        },
        return_train_score=False,
        n_jobs=1,
    )

    print(f"\n=== {name} ===")
    print(
        "Fold accuracies:",
        scores["test_accuracy"].round(4).tolist(),
    )
    print(
        "Mean accuracy:",
        round(scores["test_accuracy"].mean(), 4),
    )
    print(
        "Mean macro F1:",
        round(scores["test_macro_f1"].mean(), 4),
    )
    print(
        "Accuracy standard deviation:",
        round(scores["test_accuracy"].std(), 4),
    )

print(
    "\nReminder: cross-validation measures performance on "
    "held-out rows from this dataset only. It does not establish "
    "clinical validity or generalization to real patients."
)
