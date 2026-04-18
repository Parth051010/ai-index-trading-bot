import time

from angel_api import angel_login, get_index_price
from angel_master import get_indices

from price_store import store
from candle_engine import build_candles
from strategy import generate_signal
from paper_trader import place_trade, check_trade


def run_live_engine():

    obj = angel_login()
    indices = get_indices()

    print("TOTAL INDICES:", len(indices))
    print("Starting Live Engine...")

    MAX_PER_CYCLE = 10
    current_index = 0

    while True:

        chunk = indices.iloc[current_index:current_index + MAX_PER_CYCLE]

        if chunk.empty:
            current_index = 0
            continue

        for _, row in chunk.iterrows():

            try:
                symbol = row["symbol"]
                token = row["token"]
                exchange = row["exch_seg"]

                price = get_index_price(obj, symbol, token, exchange)

                if price is None:
                    continue

                print("PRICE:", symbol, price)

                # ✅ STORE DATA
                store.store(symbol, price)

                prices = store.get(symbol)
                print("LEN:", symbol, len(prices))

                # wait until enough data
                if len(prices) < 20:
                    continue

                df = build_candles(prices)

                if df is None or df.empty:
                    continue

                # 🧠 SIGNAL
                signal = generate_signal(df)
                print(f"{symbol} → {signal} @ {price}")

                # 💸 TRADE
                check_trade(symbol, price)
                place_trade(symbol, signal, price)

                time.sleep(0.5)

            except Exception as e:
                print(f"Error in {symbol}: {e}")

                if "Access denied" in str(e) or "Invalid" in str(e):
                    print("🔄 Re-login...")
                    obj = angel_login()

                continue

        current_index += MAX_PER_CYCLE

        print("⏳ Cooling down...")
        time.sleep(2)