
# ===============================
# 📊 PAPER TRADER (FINAL CLEAN)
# ===============================

import json
import os
from db import update_user

FILE = "account.json"

current_user = None

active_trade = None

balance = 50000
initial_balance = 50000

trade_history = []
total_trades = 0
wins = 0
losses = 0

trading_active = False


# 💾 LOAD DATA
def load_data():
    global balance, initial_balance, trade_history, total_trades, wins, losses

    if not os.path.exists(FILE):
        print("⚠️ No saved data found")
        return

    with open(FILE, "r") as f:
        data = json.load(f)

    balance = data.get("balance", 50000)
    initial_balance = data.get("initial_balance", 50000)
    trade_history = data.get("history", [])
    total_trades = data.get("total_trades", 0)
    wins = data.get("wins", 0)
    losses = data.get("losses", 0)

    print("✅ Account Loaded from file")


# 💾 SAVE DATA
def save_data():
    data = {
        "balance": balance,
        "initial_balance": initial_balance,
        "history": trade_history,
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses
    }

    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)

    print("💾 Data Saved")


# 🚀 START / STOP

def start_trading():
    global trading_active
    trading_active = True
    print("🚀 Trading Started")


def stop_trading():
    global trading_active
    trading_active = False
    print("🛑 Trading Stopped")


# 🎯 ENTER TRADE
def enter_trade(direction, price):
    global active_trade, balance

    # ✅ Risk based on CAPITAL (correct way)
    risk_amount = balance * 0.01     # 1% risk
    reward_amount = balance * 0.02   # 2% reward

    # ✅ Convert to price movement (points)
    risk = risk_amount / 100
    reward = reward_amount / 100

    if direction == "BUY":
        sl = price - risk
        target = price + reward
    else:
        sl = price + risk
        target = price - reward

    active_trade = {
        "direction": direction,
        "entry": price,
        "sl": sl,
        "target": target
    }

    print(f"🚀 TRADE ENTERED: {direction} @ {price}")
    print(f"💰 Risk: ₹{risk_amount} | Reward: ₹{reward_amount}")
    print(f"SL: {sl} | TARGET: {target}")


# 🧠 PROCESS SIGNAL
def process_signal(signal, price):
    global active_trade

    if not trading_active:
        return

    if active_trade is not None:
     print("⚠️ Trade already active, skipping new entry")
     return

    if signal == "BUY":
        enter_trade("BUY", price)

    elif signal == "SELL":
        enter_trade("SELL", price)


# 💰 CHECK TRADE EXIT
def check_trade(price):
    global active_trade, balance, trade_history, total_trades, wins, losses

    if not trading_active or active_trade is None:
        return

    entry = active_trade["entry"]
    sl = active_trade["sl"]
    target = active_trade["target"]
    direction = active_trade["direction"]

    pnl = 0
    result = ""

    if direction == "BUY":
        if price >= target:
            pnl = price - entry
            wins += 1
            result = "TARGET HIT (BUY)"
        elif price <= sl:
            pnl = price - entry
            losses += 1
            result = "SL HIT (BUY)"

    elif direction == "SELL":
        if price <= target:
            pnl = entry - price
            wins += 1
            result = "TARGET HIT (SELL)"
        elif price >= sl:
            pnl = entry - price
            losses += 1
            result = "SL HIT (SELL)"

    if pnl != 0:
        balance += pnl
        total_trades += 1

        trade_history.append({
            "direction": direction,
            "entry": entry,
            "exit": price,
            "pnl": pnl
        })

        print(f"{'💰' if pnl > 0 else '❌'} {result}")
        print(f"💰 PnL: {pnl:.2f} | Balance: {balance:.2f}")

        active_trade = None
        save_data()

def add_balance(amount):
    global balance
    balance += amount
    save_data()
    print(f"💰 Added ₹{amount} | New Balance: ₹{balance}")

# 📊 PNL DATA FOR API
def get_pnl_data():
    return {
        "balance": balance,
        "pnl": balance - initial_balance,
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "history": trade_history
    }

# 🚀 LOAD DATA ON START
load_data()