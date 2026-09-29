"""
BlockAccred - simple anomaly detection (Isolation Forest).

One small Isolation Forest is trained per assessment parameter on DEMO
historical data (training_data.csv: 6 demo programmes x 10 years each). Each data point is the year-over-year change of a value (e.g. placement
moving from 84% to 98% is a +14 change, which is unusual compared with
the normal +1 to +3 changes seen in history)

A new value is scored with score_samples(): the lower (more negative) the
score, the more unusual the value. Scores below THRESHOLD are flagged
"Requires Review". This only marks unusual patterns - it never claims fraud.

Usage:
    python anomaly_detection.py            # train + save model.joblib + demo
"""
import os
import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "training_data.csv")
MODEL_PATH = os.path.join(HERE, "model.joblib")
THRESHOLD = -0.60  # score below this => unusual


def _features(values):
    """Year-over-year change for each year: [[change], ...] (first year has no change)."""
    return [[values[i] - values[i - 1]] for i in range(1, len(values))]


def train():
    df = pd.read_csv(CSV_PATH).sort_values(["parameter", "programme", "year"])
    bundle = {"models": {}, "last_value": {}, "history": {}}
    for param, g in df.groupby("parameter"):
        X = []
        for _, pg in g.groupby("programme"):          # each demo programme is its own time series
            X += _features(pg["value"].tolist())
        model = IsolationForest(n_estimators=200, contamination="auto", random_state=42)
        model.fit(X)
        last_year = g["year"].max()
        bundle["models"][param] = model
        bundle["last_value"][param] = float(g[g["year"] == last_year]["value"].mean())
        yearly = g.groupby("year")["value"].mean().round(1)   # average trend, used for the chart
        bundle["history"][param] = [{"year": int(y), "value": float(v)} for y, v in yearly.items()]
    joblib.dump(bundle, MODEL_PATH)
    return bundle


def load():
    """Load the trained model; retrain automatically if the file is missing/incompatible."""
    try:
        return joblib.load(MODEL_PATH)
    except Exception:
        return train()


def score(parameter, value):
    bundle = load()
    model = bundle["models"][parameter]
    feats = [[value - bundle["last_value"][parameter]]]
    s = float(model.score_samples(feats)[0])
    return {"anomaly_score": round(s, 3), "is_anomaly": s < THRESHOLD}


def history(parameter=None):
    h = load()["history"]
    return h if parameter is None else h.get(parameter, [])


if __name__ == "__main__":
    train()
    print("Model trained and saved to", MODEL_PATH)
    for p, v in [("Placement", 85), ("Placement", 98), ("Faculty Information", 99),
                 ("Research/Publications", 41), ("Infrastructure", 82)]:
        r = score(p, v)
        flag = "ANOMALY - Requires Review" if r["is_anomaly"] else "normal"
        print(f"{p:24s} {v:>4}%  score={r['anomaly_score']:>7}  {flag}")
