

import pandas as pd
import numpy as np
import joblib
import os

from sklearn.ensemble import RandomForestClassifier

MODEL_PATH = "rf_model.pkl"


def load_data():
    files = [f for f in os.listdir() if f.endswith(".csv")]
    prices = []

    for f in files:
        try:
            df = pd.read_csv(f, header=None)
            prices.extend(df[0].values.tolist())
        except:
            continue

    return pd.DataFrame(prices, columns=["close"])


def create_features(df):
    df["returns"] = df["close"].pct_change()
    df["ma5"] = df["close"].rolling(5).mean()
    df["ma10"] = df["close"].rolling(10).mean()
    df["volatility"] = df["returns"].rolling(5).std()

    df["target"] = np.where(df["close"].shift(-1) > df["close"], 1, 0)

    df.dropna(inplace=True)
    return df


def train_model():
    df = load_data()

    print("📊 Total data points:", len(df))

    if len(df) < 50:
        print("❌ Not enough data")
        return

    df = create_features(df)

    print("📊 After feature engineering:", len(df))

    if len(df) < 20:
        print("❌ Not enough usable data")
        return

    X = df[["returns", "ma5", "ma10", "volatility"]]
    y = df["target"]

    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)

    print("✅ RF MODEL TRAINED & SAVED")


def predict_signal(prices):
    if not os.path.exists(MODEL_PATH):
        return "HOLD"

    model = joblib.load(MODEL_PATH)

    df = pd.DataFrame(prices, columns=["close"])
    df = create_features(df)

    if df.empty:
        return "HOLD"

    features = ["returns", "ma5", "ma10", "volatility"]

    last = pd.DataFrame(
        [df.iloc[-1][features].values],
        columns=features
    )

    pred = model.predict(last)[0]

    return "BUY" if pred == 1 else "SELL"

if __name__ == "__main__":
    train_model()