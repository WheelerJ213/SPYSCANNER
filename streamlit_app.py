import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Load SPY options
ticker = yf.Ticker("SPY")
expirations = ticker.options

# Choose today's and tomorrow's expiration dates
today = datetime.today().date()
tomorrow = today + timedelta(days=1)
target_exps = [d for d in expirations if datetime.strptime(d, '%Y-%m-%d').date() in [today, tomorrow]]

# Criteria
min_volume = 10000
min_oi = 5000
max_bid_ask_spread = 0.05

all_filtered = []

for exp_date in target_exps:
    calls = ticker.option_chain(exp_date).calls
    puts = ticker.option_chain(exp_date).puts

    for df, label in zip([calls, puts], ["Call", "Put"]):
        df = df.copy()
        df["type"] = label
        df["bid_ask_spread"] = df["ask"] - df["bid"]
        df = df[
            (df["volume"] > min_volume) &
            (df["openInterest"] > min_oi) &
            (df["bid_ask_spread"] <= max_bid_ask_spread)
        ]
        all_filtered.append(df)

result = pd.concat(all_filtered)
result = result.sort_values(by="volume", ascending=False)

# Display top 20 results
print(result[["contractSymbol", "type", "strike", "lastPrice", "bid", "ask", "volume", "openInterest", "impliedVolatility"]].head(20))
