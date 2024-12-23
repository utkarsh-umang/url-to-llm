import os
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

def get_sheet_data(spreadsheet_id, range_name, credentials_file):
    try:
        # Authenticate with the service account
        creds = service_account.Credentials.from_service_account_file(
            credentials_file,
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
        )

        # Build the Sheets API service
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        values = result.get('values', [])

        # Convert the data to a pandas DataFrame
        if not values:
            print("No data found.")
            return pd.DataFrame()
        else:
            return pd.DataFrame(values[1:], columns=values[0])

    except Exception as e:
        print(f"Error fetching data from Google Sheets: {e}")
        return pd.DataFrame()
