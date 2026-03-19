import base64
import os
import pickle
import sqlite3
from datetime import timedelta
from functools import wraps
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

import numpy as np
import pyotp
import qrcode
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, session
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
if not app.config["SECRET_KEY"]:
    raise RuntimeError("SECRET_KEY environment variable is not set")

app.config["JSON_SORT_KEYS"] = False
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("FLASK_ENV") == "production"
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["WTF_CSRF_TIME_LIMIT"] = 3600
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

csrf = CSRFProtect(app)

BASE_DIR = Path(__file__).resolve().parent
MODEL_FILE = BASE_DIR / "my_saved_poly_v3.pkl"
AUTH_DB = BASE_DIR / "auth.db"

MIN_AVG = 200
MAX_AVG = 23750


def get_db_conn():
    conn = sqlite3.connect(AUTH_DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_auth_db():
    with get_db_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                totp_secret TEXT
            )
            """
        )
        cols = {
            row["name"] for row in conn.execute("PRAGMA table_info(users)").fetchall()
        }
        if "totp_secret" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN totp_secret TEXT")

        conn.commit()


def get_user_by_email(email: str):
    with get_db_conn() as conn:
        return conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()


def get_user_by_id(user_id: int):
    with get_db_conn() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def create_user(email: str, password: str) -> bool:
    password_hash = generate_password_hash(password)
    try:
        with get_db_conn() as conn:
            conn.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (email, password_hash),
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def verify_user(email: str, password: str):
    user = get_user_by_email(email)
    if not user:
        return None
    return user if check_password_hash(user["password_hash"], password) else None


def ensure_totp_secret(user_id: int):
    user = get_user_by_id(user_id)
    if user and user["totp_secret"]:
        return user["totp_secret"]

    secret = pyotp.random_base32()
    with get_db_conn() as conn:
        conn.execute("UPDATE users SET totp_secret = ? WHERE id = ?", (secret, user_id))
        conn.commit()
    return secret


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


def make_qr_code_base64(otp_uri: str) -> str:
    qr = qrcode.QRCode(version=1, box_size=8, border=4)
    qr.add_data(otp_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    stream = BytesIO()
    img.save(stream, format="PNG")
    return base64.b64encode(stream.getvalue()).decode("utf-8")


def is_safe_next(next_url: str) -> bool:
    if not next_url:
        return False
    parsed = urlparse(next_url)
    return parsed.scheme == "" and parsed.netloc == "" and next_url.startswith("/")


def login_required_2fa(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(f"/login.html?next={request.path}")
        if not session.get("2fa_verified", False):
            return redirect("/2fa.html")
        return f(*args, **kwargs)

    return decorated


init_auth_db()
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
    return jsonify({"status": "healthy"}), 200


@app.route("/signup.html", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        if not email or not password:
            return render_template("signup.html", error="Missing fields")

        if len(password) < 8:
            return render_template(
                "signup.html", error="Password must be at least 8 characters"
            )

        if create_user(email, password):
            return render_template("login.html", is_done=True)

        return render_template("signup.html", dupe=True)

    return render_template("signup.html")


@app.route("/login.html", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        next_url = request.args.get("next", "")
        if is_safe_next(next_url):
            session["next_url"] = next_url
        return render_template("login.html")

    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""

    user = verify_user(email, password)
    if not user:
        return render_template("login.html", error="Invalid email or password")

    session.clear()
    session["pending_user_id"] = int(user["id"])
    session["pending_user_email"] = user["email"]
    # restore next_url after session.clear()
    next_url = request.args.get("next") or "/predict"
    session["next_url"] = next_url if is_safe_next(next_url) else "/predict"

    return redirect("/2fa.html")


@app.route("/2fa.html", methods=["GET", "POST"])
def two_factor_auth():
    pending_user_id = session.get("pending_user_id")
    pending_user_email = session.get("pending_user_email")

    if not pending_user_id or not pending_user_email:
        return redirect("/login.html")

    secret = ensure_totp_secret(int(pending_user_id))
    totp = pyotp.TOTP(secret)
    otp_uri = totp.provisioning_uri(
        name=pending_user_email, issuer_name="WCA Predictor"
    )
    qr_code_b64 = make_qr_code_base64(otp_uri)

    if request.method == "POST":
        otp_input = (request.form.get("otp") or "").strip()
        if totp.verify(otp_input, valid_window=1):
            session["user_id"] = int(pending_user_id)
            session["user_email"] = pending_user_email
            session["2fa_verified"] = True
            next_url = session.pop("next_url", "/")
            session.pop("pending_user_id", None)
            session.pop("pending_user_email", None)
            return redirect(next_url if is_safe_next(next_url) else "/")

        return render_template(
            "2fa.html", qr_code=qr_code_b64, error="Invalid code. Please try again"
        )

    return render_template("2fa.html", qr_code=qr_code_b64)


@app.route("/logout.html", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect("/")


@app.route("/predict", methods=["GET", "POST"])
@login_required_2fa
def predict():
    if request.method == "GET":
        raw_val = request.args.get("events_completed")
    else:
        raw_val = request.form.get("events_completed")

    if raw_val is None:
        if request.method == "GET":
            return render_template("index.html")
        return render_template("index.html", error="events_completed is required")

    try:
        events_completed = float(raw_val)
        if events_completed <= 0:
            return render_template(
                "index.html", error="events_completed must be greater than zero"
            )
    except (TypeError, ValueError):
        return render_template("index.html", error="events_completed must be a number")

    x_max = max(100, int(events_completed * 1.1) + 10)
    x_range = list(range(0, x_max + 1))
    y_range = [round(unscale(exp_func(x, A, B, C)) / 1000.0, 2) for x in x_range]

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
