import yfinance as yf
import pandas as pd

stocks = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS"
]

results = []

for stock in stocks:
    try:
        df = yf.download(stock, period="1y", progress=False)

        close = df["Close"]

        current = float(close.iloc[-1])
        sma20 = float(close.rolling(20).mean().iloc[-1])
        sma50 = float(close.rolling(50).mean().iloc[-1])

        ret_6m = ((current / float(close.iloc[-126])) - 1) * 100

        score = 0

        if current > sma20:
            score += 40

        if sma20 > sma50:
            score += 30

        score += min(max(ret_6m, 0), 30)

        results.append([stock, round(score, 2)])

    except:
        pass

result_df = pd.DataFrame(results, columns=["Stock", "Momentum Score"])

result_df = result_df.sort_values(
    by="Momentum Score",
    ascending=False
)

print(result_df)
