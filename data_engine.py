import yfinance as yf
import pandas as pd
import yfinance as yf

INDEX_SYMBOLS = {
    "NIFTY": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "SENSEX": "^BSESN",
    "FINNIFTY": "NIFTY_FIN_SERVICE.NS",
    "MIDCAP": "NIFTY_MIDCAP_100.NS"
}

def get_index_data(symbol="^NSEI"):

    df = yf.download(symbol, period="5d", interval="5m")

    if df.empty:
        print("No data fetched")
        return None

    # Flatten columns
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

    df = df.reset_index()

    # 🔥 Arrange columns properly
    df = df[["Datetime", "Open", "High", "Low", "Close", "Volume"]]


def get_data(symbol):

    df = yf.download(symbol, period="5d", interval="15m")

    if df.empty:
        return None

    # 🔥 FIX MULTI-INDEX
    if isinstance(df.columns, pd.MultiIndex):
     df.columns = df.columns.get_level_values(0)

    df = df.reset_index()

    return df