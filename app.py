from flask import Flask, request, jsonify, render_template
import threading
import time
import paper_trader
from db import create_user, get_user, update_user
from angel_api import angel_login, get_index_price, get_historical_data
from angel_master import get_indices
from price_store import store
from candle_engine import build_candles
from model_rf import predict_signal
from paper_trader import get_pnl_data
from flask import jsonify

from datetime import datetime

def load_user_data(user):
    global balance, trade_history, active_trade, current_user

    current_user = user["username"]
    balance = user.get("balance", 50000)
    trade_history = user.get("history", [])
    active_trade = user.get("active_trade", None)

    print("✅ User data loaded")

current_user = None

def is_market_open():
    now = datetime.now()

    # Weekend check
    if now.weekday() >= 5:
        return False

    current_time = now.time()

    market_start = datetime.strptime("09:15", "%H:%M").time()
    market_end = datetime.strptime("15:30", "%H:%M").time()

    return market_start <= current_time <= market_end

selected_symbol = "NIFTYBANK"   # default

SYMBOL_MAP = {
    "NIFTY": "NIFTY50",
    "BANKNIFTY": "NIFTYBANK",
    "FINNIFTY": "NIFTYFINSERVICE",

    "NIFTYIT": "NIFTYIT",
    "NIFTYFMCG": "NIFTYFMCG",
    "NIFTYAUTO": "NIFTYAUTO",
    "NIFTYPHARMA": "NIFTYPHARMA",
    "NIFTYMETAL": "NIFTYMETAL",
    "NIFTYREALTY": "NIFTYREALTY",
    "NIFTYINFRA": "NIFTYINFRA",
    "NIFTYENERGY": "NIFTYENERGY",

    "NIFTYMIDCAP100": "NIFTYMIDCAP100",
    "NIFTYNXT50": "NIFTYNEXT50",
    "NIFTY100": "NIFTY100"
}

print("📊 Starting AI Trading Bot...")

app = Flask(__name__)

obj = None
indices = None


# ✅ SYMBOL NORMALIZER (IMPORTANT)
def normalize_symbol(symbol):
    symbol = symbol.upper().strip().replace(" ", "")
    return SYMBOL_MAP.get(symbol, symbol)

# 🚀 ENGINE
def run_engine():
    global obj, indices

    obj = angel_login()
    indices = get_indices()

    print("✅ TOTAL INDICES:", len(indices))

    # =========================
    # 📊 LOAD HIST DATA
    # =========================
    print("📊 Loading historical data...")

    for i, (_, row) in enumerate(indices.iterrows()):
        try:
            symbol = normalize_symbol(row["symbol"])
            token = row["token"]
            exchange = row["exch_seg"]

            print(f"⏳ Loading {symbol} ({i+1}/14)")

            candles = get_historical_data(obj, token, exchange)

            if candles:
                for c in candles:
                    store.store(symbol, float(c[4]))

            print(f"✅ {symbol} → {len(candles) if candles else 0} candles")

            time.sleep(1)

        except Exception as e:
            print(f"❌ HIST ERROR {row['symbol']}:", e)

    print("🚀 ALL HIST DATA LOADED")

    # =========================
    # ⚡ LIVE ENGINE
    # =========================
    while True:
        for _, row in indices.iterrows():
            try:
                symbol = normalize_symbol(row["symbol"])

                # 🔥 FILTER FIRST
                if symbol != selected_symbol:
                    continue

                token = row["token"]
                exchange = row["exch_seg"]

                price = get_index_price(obj, symbol, token, exchange)

                if price is None:
                    continue

                print("PRICE:", symbol, price)

                store.store(symbol, float(price))

                prices = store.get(symbol)

                # ⛔ Skip trading if market closed
                if not is_market_open():
                    print("⛔ Market Closed - Skipping Trading")
                    time.sleep(2)
                    continue

                # =========================
                # SIGNAL LOGIC (AI - RF)
                # =========================
                signal = "HOLD"

                if prices and len(prices) > 20:
                    try:
                        signal = predict_signal(prices)
                    except:
                        signal = "HOLD"

                if not signal:
                    signal = "HOLD"

                print(f"🧠 AI SIGNAL: {symbol} → {signal}")

                # =========================
                # PAPER TRADING
                # =========================
                print("🟢 ENGINE trading_active:", paper_trader.trading_active)

                if paper_trader.trading_active:

                    if signal != "HOLD":
                        print("📢 TRYING TO ENTER TRADE...", signal)
                        paper_trader.process_signal(signal, price)

                    paper_trader.check_trade(price)

                time.sleep(2)

            except Exception as e:
                print("⚠️ LIVE ERROR:", e)

        time.sleep(3)

# 🏠 HOME
@app.route("/")
def home():
    return render_template("dashboard.html")

@app.route('/pnl-data')
def pnl_data():
    return jsonify(get_pnl_data())

@app.route("/start-trading")
def start_trading():
    from paper_trader import start_trading
    start_trading()
    return "🚀 Paper Trading Started"

@app.route("/stop-trading")
def stop_trading():
    from paper_trader import stop_trading
    stop_trading()
    return "🛑 Paper Trading Stopped"

# 💵 ADD BALANCE ENDPOINT
@app.route("/add-funds")
def add_funds():
    amount = float(request.args.get("amount", 0))
    import paper_trader
    paper_trader.add_balance(amount)
    return jsonify({"message": f"₹{amount} added successfully"})

@app.route("/set-symbol")
def set_symbol():
     global selected_symbol
     import paper_trader
     
     symbol = request.args.get("symbol", "NIFTYBANK")
     selected_symbol = normalize_symbol(symbol)

     paper_trader.active_trade = None
     print("🎯 SELECTED SYMBOL:", selected_symbol)
     return OK


# 📈 LIVE PRICE
@app.route("/live-price")
def live_price():
    try:
        symbol = normalize_symbol(request.args.get("symbol", ""))

        prices = store.get(symbol)

        if not prices or len(prices) == 0:
            return jsonify({"price": 0}), 200

        return jsonify({"price": float(prices[-1])}), 200

    except Exception as e:
        print("PRICE ERROR:", e)
        return jsonify({"price": 0}), 200


@app.route("/signup", methods=["POST"])
def signup():
    data = request.json

    success = create_user(data["username"], data["password"])

    if success:
        return jsonify({"status": "success"})
    return jsonify({"status": "user_exists"})

@app.route("/login", methods=["POST"])
def login():
    global current_user

    data = request.json
    user = get_user(data["username"])

    if user and user["password"] == data["password"]:
        current_user = user["username"]

        # 🔥 LOAD USER DATA INTO PAPER TRADER
        import paper_trader
        paper_trader.load_user_data(user)

        return jsonify({"status": "success"})

    return jsonify({"status": "fail"})


# 📊 LIVE CANDLES
@app.route("/live-candles")
def live_candles():
    try:
        symbol = normalize_symbol(request.args.get("symbol", ""))

        prices = store.get(symbol)
        current_price = prices[-1] if prices and len(prices) > 0 else None

        print("📊 REQUEST:", symbol, "| LEN:", len(prices) if prices else 0)

        if not prices or len(prices) < 5:
            return jsonify({
                "candles": [],
                "signal": "WAIT",
                "trade": {}
            }), 200

        df = build_candles(prices , candle_size=5)

        # ✅ FIX COLUMN CASE
        df.columns = df.columns.str.capitalize()

        if df.empty or "Open" not in df.columns:
            return jsonify({
                "candles": [],
                "signal": "WAIT",
                "trade": {}
            }), 200

        if not is_market_open():
            signal = "MARKET CLOSED"
        else:
            signal = predict_signal(prices)

        print("🧠 SIGNAL:", symbol, signal)

        candles = []
        now = int(time.time())

        # 🔥 Use proper sequential timestamps (latest candle = current time)
        for i, row in df.iterrows():
            candle_time = now - (len(df) - i) * 60

            candles.append({
                "time": candle_time,
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
            })


        trade_data = {}

        trade = paper_trader.active_trade

        if trade and trade.get("entry"):
            entry = trade.get("entry")
            sl = trade.get("sl")
            target = trade.get("target")
            direction = trade.get("direction")

            pnl = 0

            print("📊 ACTIVE TRADE:", trade)

            if entry and current_price:
                if direction == "BUY":
                    pnl = current_price - entry
                elif direction == "SELL":
                    pnl = entry - current_price

                trade_data = {
                    "entry": entry,
                    "sl": sl,
                    "target": target,
                    "type": direction,
                    "pnl": round(pnl, 2)
                }

        return jsonify({
            "candles": candles,
            "signal": signal,
            "trade": trade_data
        }), 200

    except Exception as e:
        print("CANDLE ERROR:", e)
        return jsonify({
            "candles": [],
            "signal": "ERROR",
            "trade": {}
        }), 200


# 🚀 START ENGINE
threading.Thread(target=run_engine, daemon=True).start()


if __name__ == "__main__":
    app.run(debug=False)