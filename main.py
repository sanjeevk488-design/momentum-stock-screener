import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import requests
import zipfile
import io
from datetime import datetime, timedelta
import os
import json

# 1. Credentials Setup
creds_json = os.environ.get('GCP_CREDENTIALS')

if not creds_json:
    print("CRITICAL: GCP_CREDENTIALS secret missing!")
    exit(1)

creds_dict = json.loads(creds_json)

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# ==============================
# GOOGLE SHEET DETAILS
# ==============================

spreadsheet_id = "1GaHFHbROav38DKvxHivoyCm3UPHIJ_-kF6qL_KCCA_s"

worksheet = client.open_by_key(spreadsheet_id).worksheet("NSE_DATA")

# ==============================
# NSE DATA FETCHER
# ==============================

def fetch_bhavcopy_for_date(date_obj):

    date_str = date_obj.strftime("%Y%m%d")

    url = f"https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_{date_str}_F_0000.csv.zip"

    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }

    try:

        print(f"Checking file for date: {date_str}")

        response = requests.get(url, headers=headers, timeout=20)

        if response.status_code == 200:

            with zipfile.ZipFile(io.BytesIO(response.content)) as z:

                csv_filename = z.namelist()[0]

                with z.open(csv_filename) as f:

                    df = pd.read_csv(f)

                    # Remove extra spaces from columns
                    df.columns = [c.strip() for c in df.columns]

                    print("Available Columns:")
                    print(df.columns.tolist())

                    # Detect required columns
                    sym_col = next((c for c in ['TckrSymb', 'SYMBOL'] if c in df.columns), None)

                    close_col = next((c for c in ['ClsPric', 'CLOSE'] if c in df.columns), None)

                    series_col = next((c for c in ['SctySrs', 'SERIES'] if c in df.columns), None)

                    turnover_col = next((
                        c for c in [
                            'TtlTrfVal',
                            'TtlTrdVal',
                            'TURNOVER_LACS',
                            'TURNOVER'
                        ] if c in df.columns
                    ), None)

                    # Validation
                    if not all([sym_col, close_col, turnover_col]):

                        print("Required columns missing!")
                        return None

                    # Only EQ series
                    if series_col:
                        df = df[df[series_col].astype(str).str.strip() == 'EQ']

                    # Remove ETFs / Gold / Liquid
                    filter_keywords = (
    'BEES|ETF|GOLD|LIQUID|NIFTY|BANK|SILVER|INDEX|PSUBNK|MNC|LOWVOL'
)

                    df = df[
                        ~df[sym_col].astype(str).str.contains(
                            filter_keywords,
                            case=False,
                            na=False
                        )
                    ]

                    # Convert turnover to numeric
                    df[turnover_col] = pd.to_numeric(
                        df[turnover_col],
                        errors='coerce'
                    )

                    df = df.dropna(subset=[turnover_col])

                    # Top 250 by Turnover
                    df_top = df.sort_values(
                        by=turnover_col,
                        ascending=False
                    ).head(250)

                    # Final data
                    final_data = df_top[
                        [sym_col, turnover_col, close_col]
                    ].values.tolist()

                    return final_data

        return None

    except Exception as e:

        print(f"NSE Fetch Error: {str(e)}")
        return None

# ==============================
# EXECUTION LOGIC
# ==============================

date = datetime.now()

data_to_insert = None

fetched_date_str = ""

for i in range(7):

    test_date = date - timedelta(days=i)

    # Skip weekends
    if test_date.weekday() >= 5:
        continue

    data_to_insert = fetch_bhavcopy_for_date(test_date)

    if data_to_insert:

        fetched_date_str = test_date.strftime('%d-%b-%Y')
        break

# ==============================
# UPDATE GOOGLE SHEET
# ==============================

if data_to_insert:

    try:

        # Clear old data
        worksheet.batch_clear(['A2:C251'])

        # Insert new data
        worksheet.update('A2', data_to_insert)

        # Status update
        ist_now = (
            datetime.utcnow() + timedelta(hours=5, minutes=30)
        ).strftime('%d-%b %H:%M')

        status_msg = (
            f"Data Date: {fetched_date_str} | "
            f"Last Update: {ist_now} (IST)"
        )

        worksheet.update('K2', [[status_msg]])

        print(
            f"SUCCESS: Sheet Updated Successfully "
            f"with Turnover Data for {fetched_date_str}!"
        )

    except Exception as e:

        print(f"Google Sheet Error: {str(e)}")

else:

    print(
        "FAILED: पिछले 7 दिनों में किसी भी दिन की फाइल नहीं मिली "
        "या प्रोसेस नहीं हुई।"
    )
