from flask import Flask, render_template, request
import pandas as pd
from datetime import datetime

app = Flask(__name__)

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
