from pathlib import Path
import pickle
import os
import numpy as np
from flask import Flask, jsonify, request, render_template
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# CSRF requires a secret key
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
if not app.config["SECRET_KEY"]:
    raise RuntimeError("SECRET_KEY environment variable is not set")
app.config["JSON_SORT_KEYS"] = False
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("FLASK_ENV") == "production"
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["WTF_CSRF_TIME_LIMIT"] = 3600  # token expires after 1 hour

csrf = CSRFProtect(app)

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


@app.after_request
def set_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


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
        return render_template("index.html", error="events_completed is required")

    try:
        events_completed = float(raw_val)
        if events_completed < 0:
            return render_template("index.html", error="events_completed must be >= 0")
    except (TypeError, ValueError):
        return render_template("index.html", error="events_completed must be a number")

    x_max = max(100, int(events_completed * 1.1) + 10)
    x_range = list(range(0, x_max + 1))
    y_range = [round(unscale(exp_func(x, A, B, C)) / 1000, 2) for x in x_range]

    y_scaled = exp_func(events_completed, A, B, C)
    y_cs = unscale(y_scaled)
    y_seconds = y_cs / 1000.0

    y_low = y_seconds * 0.90
    y_high = y_seconds * 1.10

    return render_template(
        "result.html",
        events_completed=events_completed,
        y_seconds=round(y_seconds, 2),
        y_cs=round(y_cs, 2),
        y_scaled=round(y_scaled, 6),
        y_low=round(y_low, 2),
        y_high=round(y_high, 2),
        x_range=x_range,
        y_range=y_range,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
