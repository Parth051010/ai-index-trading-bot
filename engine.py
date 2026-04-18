from data_engine import get_data, INDEX_SYMBOLS
from strategy import generate_signal

def run_engine():

    results = {}

    for name, symbol in INDEX_SYMBOLS.items():

        print(f"Fetching {name}...")

        df = get_data(symbol)

        if df is None or df.empty:
            print(f"{name} ❌ No Data")
            continue

        signal = generate_signal(df)

        # 🔥 FIX STARTS HERE
        close_series = df["Close"]

        # handle multi-column case
        if hasattr(close_series, "columns"):
            close_series = close_series.iloc[:, 0]

        price = float(close_series.iloc[-1])
        # 🔥 FIX ENDS HERE

        results[name] = {
            "symbol": symbol,
            "signal": signal,
            "price": price
        }

        print(f"{name} → {signal} @ {price}")

    return results