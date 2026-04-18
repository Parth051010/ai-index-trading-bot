import pandas as pd

def build_candles(prices, candle_size=1):

    candles = []

    for i in range(0, len(prices), candle_size):

        chunk = prices[i:i+candle_size]

        if len(chunk) < candle_size:
            continue

        candles.append({
            "open": chunk[0],
            "high": max(chunk),
            "low": min(chunk),
            "close": chunk[-1]
        })

    return pd.DataFrame(candles)