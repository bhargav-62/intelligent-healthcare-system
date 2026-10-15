
from pathlib import Path
import pandas as pd

from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import make_scorer, f1_score

BASE = Path(__file__).resolve().parent
df = pd.read_csv(BASE / "data" / "raw" / "Training.csv")
df = df.dropna(axis=1, how="all").drop_duplicates().reset_index(drop=True)

X = df.drop(columns="prognosis")
y = df["prognosis"].astype(str)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

models = {
    "Logistic Regression": make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=3000, random_state=42)
    ),
    "Shallow Decision Tree": DecisionTreeClassifier(
        max_depth=5, random_state=42
    ),
    "Random Forest": RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1
    )
}

for name, model in models.items():
    result = cross_validate(
        model,
        X,
        y,
        cv=cv,
        scoring={
            "accuracy": "accuracy",
            "macro_f1": make_scorer(
                f1_score,
                average="macro",
                zero_division=0
            )
        },
        n_jobs=1
    )

    print(f"\n{name}")
    print("Fold accuracies:", result["test_accuracy"].round(4).tolist())
    print("Mean accuracy:", round(result["test_accuracy"].mean(), 4))
    print("Mean macro F1:", round(result["test_macro_f1"].mean(), 4))
