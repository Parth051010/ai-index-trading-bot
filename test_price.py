from angel_master import get_indices
from angel_api import angel_login, get_index_price

obj = angel_login()

df = get_indices()

# take first 5 indices
for i in range(5):

    row = df.iloc[i]

    name = row["name"]
    symbol = row["symbol"]
    token = row["token"]
    exchange = row["exch_seg"]

    price = get_index_price(obj, token, symbol, exchange)

    print(f"{name} → {price}")