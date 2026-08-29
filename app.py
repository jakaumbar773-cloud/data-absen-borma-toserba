from flask import Flask, render_template, request, session, redirect, url_for, flash
import pandas as pd
from datetime import datetime
import os
from sqlalchemy import create_engine, text

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "change_this_to_a_random_secret_in_production")

# Simple credential (username=admin, password=admin1)
VALID_USER = {
    "username": "admin",
    "password": "admin1"
}

# Data source handling: prefer DATABASE_URL (Postgres/MySQL) on remote server
DATA_PATH = "data/attendance.csv"
DATABASE_URL = os.environ.get("DATABASE_URL", "")

def load_data_from_db(database_url):
    try:
        engine = create_engine(database_url, pool_pre_ping=True)
        # Try a simple select - expects a table named 'attendance'
        with engine.connect() as conn:
            # Use SQL text to protect identifiers; change if your table/schema is different
            result = conn.execute(text("SELECT name, counter, date, status FROM attendance"))
            rows = result.fetchall()
            if not rows:
                return pd.DataFrame(columns=["name", "counter", "date", "status"]) 
            df_db = pd.DataFrame(rows, columns=result.keys())
            # try to parse date column
            if "date" in df_db.columns:
                df_db["date"] = pd.to_datetime(df_db["date"], errors="coerce")
            return df_db
    except Exception as e:
        # Log error to console; caller may fallback to CSV
        print("Error connecting to database:", str(e))
        return None

# Load data (DB if configured, otherwise CSV)
if DATABASE_URL:
    df = load_data_from_db(DATABASE_URL)
    if df is None:
        print("Falling back to CSV data due to DB connection error.")
        df = pd.read_csv(DATA_PATH, parse_dates=["date"]) if os.path.exists(DATA_PATH) else pd.DataFrame(columns=["name","counter","date","status"])
else:
    df = pd.read_csv(DATA_PATH, parse_dates=["date"]) if os.path.exists(DATA_PATH) else pd.DataFrame(columns=["name","counter","date","status"])

# Utility: get unique names for dropdown
NAMES = sorted(df["name"].dropna().unique().tolist())

def refresh_names_from_df():
    global NAMES
    NAMES = sorted(df["name"].dropna().unique().tolist())


def filter_data(name=None, counter=None, start_date=None, end_date=None):
    d = df.copy()
    if name:
        d = d[d["name"] == name]
    if counter:
        try:
            counter_int = int(counter)
            d = d[d["counter"] == counter_int]
        except ValueError:
            pass
    if start_date:
        try:
            sd = pd.to_datetime(start_date)
            d = d[d["date"] >= sd]
        except Exception:
            pass
    if end_date:
        try:
            ed = pd.to_datetime(end_date)
            d = d[d["date"] <= ed]
        except Exception:
            pass
    d = d.sort_values("date")
    return d

# Require login for protected routes
@app.before_request
def require_login():
    # Allow access to login page, static files and favicon without auth
    allowed_endpoints = ["login", "static"]
    if request.endpoint in allowed_endpoints:
        return
    if not session.get("user"):
        return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if username == VALID_USER["username"] and password == VALID_USER["password"]:
            session["user"] = username
            flash("Berhasil login.", "success")
            return redirect(url_for("index"))
        else:
            flash("Username atau password salah.", "error")
            return render_template("login.html", username=username)

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Anda telah logout.", "info")
    return redirect(url_for("login"))

@app.route("/reload-data")
def reload_data():
    """Endpoint untuk memaksa reload data dari sumber (DB atau CSV). Berguna saat DB remote diperbarui.
    Hanya tersedia saat user sudah login."""
    global df
    if DATABASE_URL:
        new_df = load_data_from_db(DATABASE_URL)
        if new_df is not None:
            df = new_df
            refresh_names_from_df()
            flash("Data berhasil diambil dari database.", "success")
        else:
            flash("Gagal mengambil data dari database; tetap menggunakan data lokal.", "error")
    else:
        if os.path.exists(DATA_PATH):
            df = pd.read_csv(DATA_PATH, parse_dates=["date"]) 
            refresh_names_from_df()
            flash("Data berhasil dimuat dari CSV lokal.", "success")
        else:
            flash("Tidak ada sumber data yang ditemukan.", "error")
    return redirect(url_for("index"))

@app.route("/", methods=["GET"])
def index():
    # read query params for filtering
    name = request.args.get("name", "").strip()
    counter = request.args.get("counter", "").strip()
    start = request.args.get("start", "").strip()
    end = request.args.get("end", "").strip()

    filtered = None
    if any([name, counter, start, end]):
        filtered = filter_data(name=name or None,
                               counter=counter or None,
                               start_date=start or None,
                               end_date=end or None)
        # convert to records for rendering
        records = filtered.to_dict(orient="records")
    else:
        records = []

    return render_template("index.html",
                           names=NAMES,
                           records=records,
                           selected_name=name,
                           selected_counter=counter,
                           start_date=start,
                           end_date=end,
                           count=len(records))

if __name__ == "__main__":
    # Bind to 0.0.0.0 if you want to access from other machines in the network
    host = os.environ.get("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.environ.get("FLASK_RUN_PORT", "5000"))
    app.run(debug=True, host=host, port=port)
