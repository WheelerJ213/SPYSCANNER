import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Load SPY options
ticker = yf.Ticker("SPY")
expirations = ticker.options

# Get today's and tomorrow's expiration
today = datetime.today().date()
tomorrow = today + timedelta(days=1)
target_exps = [d for d in expirations if datetime.strptime(d, '%Y-%m-%d').date() in [today, tomorrow]]

# Filter settings
min_volume = 10000
min_oi = 5000
max_bid_ask_spread = 0.05

filtered_options = []

for exp_date in target_exps:
    calls = ticker.option_chain(exp_date).calls
    puts = ticker.option_chain(exp_date).puts

    for df, opt_type in zip([calls, puts], ["Call", "Put"]):
        df = df.copy()
        df["type"] = opt_type
        df["expirationDate"] = exp_date
        df["bid_ask_spread"] = df["ask"] - df["bid"]
        df = df[
            (df["volume"] > min_volume) &
            (df["openInterest"] > min_oi) &
            (df["bid_ask_spread"] <= max_bid_ask_spread)
        ]
        filtered_options.append(df)

# Combine and sort
result = pd.concat(filtered_options)
result = result.sort_values(by="volume", ascending=False)

# Estimate Max Pain = Strike with highest combined OI
max_pain_data = result.groupby("strike")["openInterest"].sum().reset_index()
max_pain = max_pain_data.sort_values("openInterest", ascending=False).iloc[0]

# Display Results
print("\nTop 20 SPY Options by Volume:")
print(result[["contractSymbol", "type", "strike", "lastPrice", "bid", "ask", "volume", "openInterest", "impliedVolatility", "expirationDate"]].head(20))

print(f"\n📍 Estimated Max Pain: ${max_pain['strike']} (Combined OI: {max_pain['openInterest']:,})")
