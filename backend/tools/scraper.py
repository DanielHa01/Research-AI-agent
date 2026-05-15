"""
Tool: Page Scraper
Fetches a URL and extracts clean text content using BeautifulSoup.
Strips scripts, styles, and nav elements.
Returns plain text capped at ~3000 words to stay within LLM context.
"""

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; ResearchAgent/1.0)"
    )
}
WORD_LIMIT = 3000

def scrape_page(url: str) -> str:
    """
    Fetch and extract readable text from a URL.
    Returns empty string on failure (fail-safe).
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=8)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        words = text.split()
        return " ".join(words[:WORD_LIMIT])
    except Exception:
        return ""
