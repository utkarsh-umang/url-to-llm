import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_about_us_link(homepage_url):
    try:
        response = requests.get(homepage_url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for an "About Us" link
        for a_tag in soup.find_all('a', href=True):
            if "about" in a_tag.text.lower() or "about" in a_tag['href'].lower():
                return urljoin(homepage_url, a_tag['href'])
        return None
    except Exception as e:
        print(f"Error scraping homepage {homepage_url}: {e}")
        return None
