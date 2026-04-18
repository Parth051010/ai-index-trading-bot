import pandas as pd
import ta


def generate_signal(df):

    if df is None or df.empty:
        return "HOLD"

    # Ensure enough data
    if len(df) < 50:
        return "HOLD"
    
    df["Close"] = df["Close"].astype(float)

    # Indicators
    df["rsi"] = ta.momentum.RSIIndicator(df["Close"], window=14).rsi()

    df["ema9"] = ta.trend.EMAIndicator(df["Close"], window=9).ema_indicator()
    df["ema21"] = ta.trend.EMAIndicator(df["Close"], window=21).ema_indicator()

    macd = ta.trend.MACD(df["Close"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()

    last = df.iloc[-1]

    # 🟢 BUY CONDITION
    if (
        last["rsi"] < 30 and
        last["ema9"] > last["ema21"] and
        last["macd"] > last["macd_signal"]
    ):
        return "BUY"

    # 🔴 SELL CONDITION
    elif (
        last["rsi"] > 70 and
        last["ema9"] < last["ema21"] and
        last["macd"] < last["macd_signal"]
    ):
        return "SELL"

    return "HOLD"