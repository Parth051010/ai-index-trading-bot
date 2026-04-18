import requests
import pandas as pd
import os
import json

# 🔹 Load full instrument list
def load_instruments():

    # ✅ CACHE FILE
    if os.path.exists("instruments.json"):
        print("⚡ Loading instruments from cache...")
        with open("instruments.json", "r") as f:
            data = json.load(f)
            return pd.DataFrame(data)

    print("🌐 Fetching instruments from API...")

    url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"

    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        # ✅ SAVE CACHE
        with open("instruments.json", "w") as f:
            json.dump(data, f)

        return pd.DataFrame(data)

    except Exception as e:
        print("⚠️ Failed to fetch instruments:", e)
        return pd.DataFrame()


# 🔹 Filter only indices
def get_indices():

    df = load_instruments()

    if df.empty:
        print("❌ No instrument data")
        return pd.DataFrame()

    indices = df[df["instrumenttype"] == "AMXIDX"].copy()

    priority = [
        "NIFTY",
        "BANKNIFTY",
        "FINNIFTY",
        "NIFTY IT",
        "NIFTY FMCG",
        "NIFTY AUTO",
        "NIFTY PHARMA",
        "NIFTY METAL",
        "NIFTY REALTY",
        "NIFTY INFRA",
        "NIFTY ENERGY",
        "NIFTY MIDCAP 100",
        "NIFTYNXT50",
        "NIFTY 100"
    ]

    # ✅ CLEAN NAMES
    indices["name_clean"] = indices["name"].astype(str).str.upper().str.strip()

    indices = indices[
        indices["name_clean"].isin([p.upper() for p in priority])
    ]

    print("✅ SELECTED INDICES:", indices["name"].tolist())
    print("TOTAL:", len(indices))

    return indices[["name", "symbol", "token", "exch_seg"]]