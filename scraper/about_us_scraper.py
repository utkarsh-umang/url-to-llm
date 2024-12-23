import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scrape_about_us_content(about_url):
    try:
        response = requests.get(about_url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract all paragraphs
        paragraphs = soup.find_all('p')
        content = " ".join(p.text.strip() for p in paragraphs if p.text.strip())
        return content
    except Exception as e:
        print(f"Error scraping 'About Us' page {about_url}: {e}")
        return None
