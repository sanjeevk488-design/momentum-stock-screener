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
        print(f"Processing {stock}")

        df = yf.download(
            stock,
            period="1y",
            auto_adjust=True,
            progress=False
        )

        if len(df) < 130:
            continue

        current = df["Close"].iloc[-1]
        sma20 = df["Close"].rolling(20).mean().iloc[-1]
        sma50 = df["Close"].rolling(50).mean().iloc[-1]

        ret_1m = ((current / df["Close"].iloc[-21]) - 1) * 100
        ret_3m = ((current / df["Close"].iloc[-63]) - 1) * 100
        ret_6m = ((current / df["Close"].iloc[-126]) - 1) * 100

        rs_score = (
            ret_1m * 0.20 +
            ret_3m * 0.30 +
            ret_6m * 0.50
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
            round(float(current), 2),
            round(float(ret_1m), 2),
            round(float(ret_3m), 2),
            round(float(ret_6m), 2),
            round(float(rs_score), 2),
            round(float(score), 2),
            signal
        ])

    except Exception as e:
        print(f"{stock} Error: {e}")

result_df = pd.DataFrame(
    results,
    columns=[
        "Symbol",
        "Close",
        "1M Return",
        "3M Return",
        "6M Return",
        "RS Score",
        "Score",
        "Signal"
    ]
)

if not result_df.empty:
    result_df = result_df.sort_values(
        by="Score",
        ascending=False
    )

print("\n===== MOMENTUM RANKING =====\n")
print(result_df.to_string(index=False))
