import re
import requests
from bs4 import BeautifulSoup
from datetime import date

def load_sites():
    with open("sites.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def get_tags(recipe_url):
    """Try to extract tags from a recipe page"""
    try:
        r = requests.get(recipe_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
    except Exception:
        return []
    
    soup = BeautifulSoup(r.text, "html.parser")
    tags = []

    # AllRecipes usually has tags in <a> elements with "taxonomy-term" or "link" class
    for tag in soup.select("a[class*='taxonomy'] , a[class*='link']"):
        t = tag.get_text(strip=True)
        if len(t) > 2 and t.lower() not in ("home", "recipes", "login", "sign up"):
            tags.append(t)
    return list(set(tags))[:5]  # limit to 5 tags

def scrape_recipes(sites):
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
                tags = get_tags(href)
                tag_text = f"  - Tags: {', '.join(tags)}" if tags else ""
                recipes.append(f"- [{title}]({href})\n{tag_text}\n")
    return recipes

if __name__ == "__main__":
    sites = load_sites()
    recipes = scrape_recipes(sites)

    with open("weekly_recipes.md", "a", encoding="utf-8") as f:
        f.write(f"\n\n## Week of {date.today():%B %d, %Y}\n\n")
        for recipe in recipes[:25]:
            f.write(recipe + "\n")

    print("✅ Weekly recipes updated successfully.")
