import gspread
from google.oauth2.service_account import Credentials
from config import SHEET_ID

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_sheet():
    creds = Credentials.from_service_account_file(
        "credentials.json",
        scopes=SCOPES
    )

    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SHEET_ID)

    return spreadsheet
