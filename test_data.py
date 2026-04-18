from data_engine import get_index_data

df = get_index_data("^NSEI")  # NIFTY

print(df.tail())