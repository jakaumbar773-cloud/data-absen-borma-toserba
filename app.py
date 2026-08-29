from flask import Flask, render_template, request, session, redirect, url_for, flash
import pandas as pd
from datetime import datetime

app = Flask(__name__)
app.secret_key = "change_this_to_a_random_secret_in_production"

# Simple credential (username=admin, password=admin1)
VALID_USER = {
    "username": "admin",
    "password": "admin1"
}

# Load sample attendance data (CSV). Replace with DB if diperlukan.
DATA_PATH = "data/attendance.csv"
df = pd.read_csv(DATA_PATH, parse_dates=["date"])

# Utility: get unique names for dropdown
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
    app.run(debug=True)
