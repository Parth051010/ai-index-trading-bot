class PriceStore:
    def __init__(self):
        self.data = {}

    def store(self, symbol, price):
        if symbol not in self.data:
            self.data[symbol] = []

        self.data[symbol].append(price)

        # keep last 200 points only
        if len(self.data[symbol]) > 200:
            self.data[symbol] = self.data[symbol][-200:]

        # ✅ SAVE TO CSV
        import csv
        with open(f"{symbol}.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([price])

    def get(self, symbol):
        return self.data.get(symbol, [])
        

store = PriceStore()