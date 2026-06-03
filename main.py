import pandas as pd
import yfinance as yf

stocks = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "SBIN.NS"
]

results = []

for stock in stocks:
    try:
        df = yf.download(stock, period="1y", progress=False)

        close = df["Close"]

        current = float(close.iloc[-1])
        sma20 = float(close.rolling(20).mean().iloc[-1])
        sma50 = float(close.rolling(50).mean().iloc[-1])

        ret_1m = ((current / float(close.iloc[-21])) - 1) * 100
        ret_3m = ((current / float(close.iloc[-63])) - 1) * 100
        ret_6m = ((current / float(close.iloc[-126])) - 1) * 100

        rs_score = round(
            (ret_1m * 0.2) +
            (ret_3m * 0.3) +
            (ret_6m * 0.5),
            2
        )

        score = 0

        if current > sma20:
            score += 40

        if sma20 > sma50:
            score += 30

        score += min(max(rs_score, 0), 30)

        signal = "BUY" if score >= 70 else "WATCH"

        results.append([
            stock,
            round(ret_1m, 2),
            round(ret_3m, 2),
            round(ret_6m, 2),
            rs_score,
            round(score, 2),
            signal
        ])

    except Exception as e:
        print(stock, e)

result_df = pd.DataFrame(
    results,
    columns=[
        "Symbol",
        "1M Return",
        "3M Return",
        "6M Return",
        "RS Score",
        "Score",
        "Signal"
    ]
)

result_df = result_df.sort_values(
    by="Score",
    ascending=False
)

print(result_df)
