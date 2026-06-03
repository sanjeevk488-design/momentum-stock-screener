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
print(result_df.to_string(index=False))from sheet_writer import get_sheet

print("\n===== MOMENTUM RANKING =====\n")
print(result_df.to_string(index=False))

try:
    spreadsheet = get_sheet()

    # NSE_DATA
    nse_sheet = spreadsheet.worksheet("NSE_DATA")
    nse_sheet.clear()

    nse_data = [["SYMBOL", "CLOSE", "RS SCORE", "SCORE", "SIGNAL"]]

    for _, row in result_df.iterrows():
        nse_data.append([
            row["Symbol"],
            row["Close"],
            row["RS Score"],
            row["Score"],
            row["Signal"]
        ])

    nse_sheet.update("A1", nse_data)

    # RS_SCORE
    rs_sheet = spreadsheet.worksheet("RS_SCORE")
    rs_sheet.clear()

    rs_data = [["SYMBOL", "1M RET", "3M RET", "6M RET", "RS SCORE"]]

    for _, row in result_df.iterrows():
        rs_data.append([
            row["Symbol"],
            row["1M Return"],
            row["3M Return"],
            row["6M Return"],
            row["RS Score"]
        ])

    rs_sheet.update("A1", rs_data)

    # TOP_BUYS
    top_sheet = spreadsheet.worksheet("TOP_BUYS")
    top_sheet.clear()

    top_df = result_df[result_df["Signal"] == "BUY"].head(25)

    top_data = [["RANK", "SYMBOL", "SCORE", "SIGNAL"]]

    rank = 1
    for _, row in top_df.iterrows():
        top_data.append([
            rank,
            row["Symbol"],
            row["Score"],
            row["Signal"]
        ])
        rank += 1

    top_sheet.update("A1", top_data)

    print("✅ Google Sheet Updated Successfully")

except Exception as e:
    print("❌ Sheet Update Error:", e)
