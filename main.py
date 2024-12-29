from data.google_sheet_parser import get_sheet_data, setup_google_sheets_service, update_sheet_values
from llm_utils.gpt_connector import process_with_gpt
from utils.helpers import process_url
import logging
import sys
import os
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

load_dotenv()

def main():
    credentials_file = "data/url-to-email-445616-cebe4868914f.json"
    spreadsheet_id = "1148jPgP8FSiBC_uB8yuTy0V5VAB_bdfwlN4JS9ZP92s"
    urls_range = "Sheet1!C:C"
    openai_api_key = os.getenv('OPENAI_API_KEY')

    # Custom prompt for GPT
    gpt_prompt = """
    Analyze the following website content and extract:
    1. The main business/organization type
    2. Key products or services
    3. Target audience or market
    
    Format the response as:
    Business Type: [type]
    Products/Services: [key offerings]
    Target Market: [audience]
    """

    try:
        service = setup_google_sheets_service(credentials_file)
        logging.info("Fetching data from Google Sheets...")
        urls_df = get_sheet_data(spreadsheet_id, urls_range, credentials_file)
        if urls_df.empty:
            logging.warning("No data found in the spreadsheet.")
            return

        # PHASE 1: Scrape URLs and write content immediately
        logging.info("Phase 1: Starting URL scraping...")
        total_urls = len(urls_df['Website'])
        for idx, url in enumerate(urls_df['Website'], 1):
            try:
                logging.info(f"Scraping URL {idx}/{total_urls}: {url}")
                content_result = process_url(url)
                content_to_write = [[str(content_result) if content_result is not None else ""]]
                update_sheet_values(service, spreadsheet_id, f"Sheet1!J{idx+1}:J{idx+1}", content_to_write)
                logging.info(f"Successfully scraped and stored content for URL {idx}")
            except Exception as e:
                error_message = f"Error: {str(e)}"
                logging.error(f"Error scraping URL at row {idx+1}: {error_message}")
                update_sheet_values(service, spreadsheet_id, f"Sheet1!J{idx+1}", [[error_message]])
        logging.info("Phase 1 completed: All URLs scraped and content stored.")

        # PHASE 2: Process with GPT
        logging.info("Phase 2: Starting GPT processing...")
        content_data = get_sheet_data(spreadsheet_id, "Sheet1!J2:J", credentials_file)
        for idx, content_row in enumerate(content_data.values, 1):
            try:
                content = content_row[0] if content_row else "No content"
                if content and not content.startswith("Error"):
                    logging.info(f"Processing content with GPT {idx}/{total_urls}")
                    gpt_result = process_with_gpt(content, gpt_prompt, openai_api_key)
                    update_sheet_values(service, spreadsheet_id, f"Sheet1!K{idx+1}:K{idx+1}", [[str(gpt_result)]])
                    logging.info(f"Successfully processed and stored GPT result for row {idx}")
                else:
                    logging.warning(f"Skipping GPT processing for row {idx} due to invalid content")
                    update_sheet_values(service, spreadsheet_id, f"Sheet1!K{idx+1}", [["No valid content to analyze"]])
            except Exception as e:
                error_message = f"GPT Error: {str(e)}"
                logging.error(f"Error in GPT processing for row {idx}: {error_message}")
                update_sheet_values(service, spreadsheet_id, f"Sheet1!K{idx+1}", [[error_message]])
        logging.info("Phase 2 completed: All content processed with GPT.")
        logging.info("Script completed successfully")
    except Exception as e:
        logging.error(f"Script failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()