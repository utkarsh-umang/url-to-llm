from data.google_sheet_parser import get_sheet_data, setup_google_sheets_service, update_sheet_values
from utils.helpers import process_url
import logging
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def main():
    credentials_file = "data/url-to-email-445616-cebe4868914f.json"
    spreadsheet_id = "1148jPgP8FSiBC_uB8yuTy0V5VAB_bdfwlN4JS9ZP92s"
    urls_range = "Sheet1!C:C"
    output_range = "Sheet1!J2"

    try:
        service = setup_google_sheets_service(credentials_file)
        logging.info("Fetching data from Google Sheets...")
        urls_df = get_sheet_data(spreadsheet_id, urls_range, credentials_file)
        if urls_df.empty:
            logging.warning("No data found in the spreadsheet.")
            return
        values = []
        total_urls = len(urls_df['Website'])
        for idx, url in enumerate(urls_df['Website'], 1):
            try:
                logging.info(f"Processing URL {idx}/{total_urls}")
                result = process_url(url)
                values.append(result)
            except Exception as e:
                logging.error(f"Error processing row {idx+1}: {str(e)}")
                values.append([f"Error: {str(e)}"])
        if not values:
            logging.warning("No values to update in the sheet")
            return
        logging.info(f"Attempting to update {len(values)} rows in Google Sheet...")
        update_sheet_values(service, spreadsheet_id, output_range, values)
        logging.info("Script completed successfully")
    except Exception as e:
        logging.error(f"Script failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()