
from pathlib import Path
from datetime import datetime, timezone

import joblib
import pandas as pd
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "baseline_symptom_model.joblib"

app = Flask(__name__)
CORS(app)

model = None
feature_names = []
model_classes = []

try:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found at {MODEL_PATH}. "
            "Run train_baseline.py first."
        )

    model = joblib.load(MODEL_PATH)

    if not hasattr(model, "feature_names_in_"):
        raise RuntimeError(
            "Model feature names are missing. "
            "Retrain the model using a pandas DataFrame."
        )

    feature_names = list(model.feature_names_in_)
    model_classes = [str(value) for value in model.classes_]

    print(f"Loaded model: {MODEL_PATH}")
    print(f"Expected symptom features: {len(feature_names)}")
    print(f"Available disease classes: {len(model_classes)}")

except Exception as exc:
    print(f"Model loading failed: {type(exc).__name__}: {exc}")


@app.route("/")
def home():
    symptoms = [
        {
            "name": name,
            "label": name.replace("_", " ").strip().capitalize(),
        }
        for name in feature_names
    ]

    return render_template(
        "index.html",
        symptoms=symptoms,
        model_loaded=model is not None,
    )


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy" if model is not None else "degraded",
        "model_loaded": model is not None,
        "feature_count": len(feature_names),
        "message": (
            "Educational prototype only; "
            "not for medical diagnosis or treatment."
        ),
    }), (200 if model is not None else 503)


@app.route("/models", methods=["GET"])
def list_models():
    return jsonify({
        "available_models": (
            ["random_forest_baseline"] if model is not None else []
        ),
        "current_model": "baseline_symptom_model",
        "symptom_features": len(feature_names),
        "disease_classes": len(model_classes),
    })


@app.route("/predict", methods=["POST", "OPTIONS"])
def predict():
    if request.method == "OPTIONS":
        return ("", 204)

    if model is None:
        return jsonify({
            "success": False,
            "message": (
                "The baseline model is unavailable. "
                "Check the Flask terminal."
            ),
        }), 503

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Send a JSON object containing a symptoms list.",
        }), 400

    selected = data.get("symptoms", [])

    if (
        not isinstance(selected, list)
        or not all(isinstance(s, str) for s in selected)
    ):
        return jsonify({
            "success": False,
            "message": "'symptoms' must be a list of symptom names.",
        }), 400

    # Reject requests with no selected symptoms.
    if not selected:
        return jsonify({
            "success": False,
            "message": (
                "Select at least one symptom to run "
                "the educational demonstration."
            ),
        }), 400

    selected_set = set(selected)
    unknown = sorted(selected_set - set(feature_names))

    if unknown:
        return jsonify({
            "success": False,
            "message": "One or more symptoms are not recognized.",
            "unknown_symptoms": unknown,
        }), 400

    # Match the exact feature names and order used during training.
    row = {
        name: int(name in selected_set)
        for name in feature_names
    }

    input_df = pd.DataFrame(
        [row],
        columns=feature_names,
    )

    try:
        predicted_label = str(model.predict(input_df)[0])
        top_predictions = []

        if hasattr(model, "predict_proba"):
            scores = model.predict_proba(input_df)[0]
            order = scores.argsort()[::-1][:5]

            for idx in order:
                top_predictions.append({
                    "disease": str(model.classes_[idx]),
                    "score": round(float(scores[idx]) * 100, 2),
                })
        else:
            top_predictions.append({
                "disease": predicted_label,
                "score": None,
            })

        # This is a safety notice, not a medical risk assessment.
        urgent_symptoms = {
            "difficulty_breathing",
            "chest_pain",
            "slurred_speech",
            "weakness_of_one_body_side",
            "coma",
        }

        urgent_notice = bool(selected_set & urgent_symptoms)

        return jsonify({
            "success": True,
            "educational_prediction": predicted_label,
            "model_scores": top_predictions,
            "model_used": "Random Forest baseline",
            "selected_symptoms": selected,
            "urgent_notice": urgent_notice,
            "disclaimer": (
                "Educational pattern-matching output only. "
                "This is not a diagnosis and must not be used "
                "to choose medicines or delay professional care."
            ),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }), 200

    except Exception as exc:
        app.logger.exception("Prediction failed")

        return jsonify({
            "success": False,
            "message": "Prediction failed. Check the Flask terminal.",
            "error_type": type(exc).__name__,
        }), 500


if __name__ == "__main__":
    print("MediCare AI educational prototype")
    print("Open http://127.0.0.1:5000")

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000,
    )
