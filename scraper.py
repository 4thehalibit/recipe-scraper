import re
import requests
from bs4 import BeautifulSoup
from datetime import date

def load_sites():
    """Load site URLs from sites.txt"""
    with open("sites.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def scrape_recipes(sites):
    """Scrape all recipe titles and links from each site"""
    recipes = []

    for site in sites:
        print(f"Scraping: {site}")
        try:
            r = requests.get(site, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            r.raise_for_status()
        except Exception as e:
            print(f"⚠️ Failed to load {site}: {e}")
            continue

        soup = BeautifulSoup(r.text, "html.parser")
        for link in soup.select("a[href*='/recipe/']"):
            title = link.get_text(strip=True)
            title = re.sub(r'\d+\s*(Ratings|Reviews)?$', '', title).strip()
            href = link.get("href")

            if title and href and href.startswith("http"):
                recipes.append(f"- [{title}]({href})")

    return recipes

if __name__ == "__main__":
    sites = load_sites()
    recipes = scrape_recipes(sites)

    with open("weekly_recipes.md", "a", encoding="utf-8") as f:
        f.write(f"\n\n## Week of {date.today():%B %d, %Y}\n\n")
        f.write("_Automatically updated every Monday_\n\n")
        for recipe in recipes[:30]:  # limit to 30 results
            f.write(recipe
