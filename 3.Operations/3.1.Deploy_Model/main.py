from pathlib import Path
import pickle
import numpy as np
from flask import Flask, jsonify, request

app = Flask(__name__)

# Optional: keep consistent secure defaults
app.config["JSON_SORT_KEYS"] = False
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


BASE_DIR = Path(__file__).resolve().parent
MODEL_FILE = BASE_DIR / "my_saved_poly_v3.pkl"


MIN_AVG = 200
MAX_AVG = 23750


def exp_func(x, a, b, c):
    return a * np.exp(-b * x) + c


def unscale(scaled_val):
    return float(scaled_val) * (MAX_AVG - MIN_AVG) + MIN_AVG


def load_model_params():
    if not MODEL_FILE.exists():
        raise FileNotFoundError(f"Model file not found: {MODEL_FILE}")
    with open(MODEL_FILE, "rb") as f:
        model_data = pickle.load(f)
    return float(model_data["a"]), float(model_data["b"]), float(model_data["c"])


A, B, C = load_model_params()


@app.route("/", methods=["GET"])
def index():
    return jsonify(
        {
            "service": "WCA exponential model API",
            "status": "ok",
            "endpoints": ["/health", "/predict?events_completed=4"],
        }
    )


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "model_file": str(MODEL_FILE.name)}), 200


@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "GET":
        raw_val = request.args.get("events_completed", None)
    else:
        if request.is_json:
            raw_val = (request.get_json(silent=True) or {}).get("events_completed")
        else:
            raw_val = request.form.get("events_completed", None)

    if raw_val is None:
        return jsonify({"error": "events_completed is required"}), 400

    try:
        events_completed = float(raw_val)
        if events_completed < 0:
            return jsonify({"error": "events_completed must be >= 0"}), 400
    except (TypeError, ValueError):
        return jsonify({"error": "events_completed must be numeric"}), 400

    y_scaled = exp_func(events_completed, A, B, C)
    y_unscaled_centiseconds = unscale(y_scaled)
    y_unscaled_seconds = y_unscaled_centiseconds / 1000.0

    return jsonify(
        {
            "input": {"events_completed": events_completed},
            "prediction": {
                "average_scaled_0_to_1": float(y_scaled),
                "average_centiseconds": y_unscaled_centiseconds,
                "average_seconds": y_unscaled_seconds,
            },
            "model": {"type": "exponential_decay", "a": A, "b": B, "c": C},
        }
    )


if __name__ == "__main__":
    # Use debug=False for safer deployment defaults
    app.run(host="0.0.0.0", port=5000, debug=False)
