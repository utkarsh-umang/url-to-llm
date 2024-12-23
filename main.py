from data.google_sheet_parser import get_sheet_data
from scraper.homepage_scraper import get_about_us_link
from scraper.about_us_scraper import scrape_about_us_content
import pandas as pd

def main():
    # Google Sheets Setup
    credentials_file = "data/url-to-email-445616-cebe4868914f.json"
    spreadsheet_id = "1148jPgP8FSiBC_uB8yuTy0V5VAB_bdfwlN4JS9ZP92s"
    range_name = "Sheet1!C:C"

    # Fetch data from Google Sheets
    print("Fetching data from Google Sheets...")
    urls_df = get_sheet_data(spreadsheet_id, range_name, credentials_file)

    if urls_df.empty:
        print("No data found in the spreadsheet.")
        return

    output_data = []

    for url in urls_df['Website']:
        print(f"Processing {url}...")
        about_link = get_about_us_link(url)
        if about_link:
            print(f"Found 'About Us' page: {about_link}")
            about_content = scrape_about_us_content(about_link)
        else:
            print("No 'About Us' page found. Falling back to homepage content.")
            about_content = scrape_about_us_content(url)

        output_data.append({"url": url, "about_content": about_content})

    # Save results to a CSV
    output_file = "data/output_emails.csv"
    pd.DataFrame(output_data).to_csv(output_file, index=False)
    print(f"Output saved to {output_file}")

if __name__ == "__main__":
    main()
