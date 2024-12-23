import pandas as pd
from scraper.homepage_scraper import get_about_us_link
from scraper.about_us_scraper import scrape_about_us_content

def main():
    # Load URLs
    input_file = "data/input_urls.csv"
    output_file = "data/output_emails.csv"

    urls = pd.read_csv(input_file)
    output_data = []

    for url in urls['url']:
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
    pd.DataFrame(output_data).to_csv(output_file, index=False)
    print(f"Output saved to {output_file}")

if __name__ == "__main__":
    main()
