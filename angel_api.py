from SmartApi.smartConnect import SmartConnect
import pyotp
from datetime import datetime, timedelta

API_KEY = "Es2lk33b"
CLIENT_ID = "V57664897"
PASSWORD = "1644"
TOTP_SECRET = "ATCTSIWE7CXBHTLSDEI65WJC24"


def angel_login():

    obj = SmartConnect(api_key=API_KEY)

    totp = pyotp.TOTP(TOTP_SECRET).now()

    data = obj.generateSession(CLIENT_ID, PASSWORD, totp)

    if not data["status"]:
        raise Exception("Login Failed")

    print("Angel Login Successful ✅")

    return obj


def get_index_price(obj, symbol, token, exchange):

    try:
        data = obj.ltpData(exchange, symbol, token)

        if data["data"] is None:
            return None

        return data["data"]["ltp"]

    except Exception as e:
        print("Error:", e)
        return None
    
    
    

def get_historical_data(obj, token, exchange):
    try:
        # 🔥 Get last 5 days data (more candles for ML)
        to_date = datetime.now()
        from_date = to_date - timedelta(days=5)

        params = {
            "exchange": exchange,
            "symboltoken": token,
            "interval": "ONE_MINUTE",
            "fromdate": from_date.strftime("%Y-%m-%d %H:%M"),
            "todate": to_date.strftime("%Y-%m-%d %H:%M")
        }

        response = obj.getCandleData(params)

        # ✅ Validate response
        if not response or "data" not in response:
            print("⚠️ No historical data received")
            return []

        candles = response["data"]

        if not candles:
            print("⚠️ Empty candles data")
            return []

        print(f"✅ Loaded {len(candles)} candles")

        # 🔥 Return raw candles (fix for downstream engine compatibility)
        return candles

    except Exception as e:
        print("❌ HIST ERROR:", e)
        return []