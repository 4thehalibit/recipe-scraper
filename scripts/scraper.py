import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import os

SITES_FILE = "data/sites.txt"
OUTPUT_FILE = "recipes/weekly_recipes.md"
FALLBACK_IMG = "assets/fallback.png"

HEADER = """<link rel="stylesheet" href="../assets/style.css?v=3">

<div class="nav">
  <a href="../index.md" class="nav-btn">🏠 Home</a>
  <a href="../recipes/weekly_recipes.md" class="nav-btn">🥘 Weekly Recipes</a>
  <a href="../recipes/my_recipes.md" class="nav-btn">👨‍🍳 My Recipes</a>
</div>

<div class="header">
  <a href="../index.md" class="title">🍴 Recipe Scraper</a>
  <span class="subtitle">Weekly Auto-Generated Dinners</span>
</div>

# 🥘 Weekly Recipes

These recipes are scraped automatically every Monday morning.
Designed for 2–3 servings, they focus on simplicity and great flavor.

---
"""


def clean_url(url):
    return url.split("?")[0].rstrip("/")

def extract_tags(soup):
    tags = set()
    tag_areas = soup.select("a.recipe-category-link, span.mntl-taxonomy-list-item, span.mntl-recipe-taxonomy")
    for t in tag_areas:
        txt = t.get_text(strip=True)
        if txt and len(txt) < 25:
            tags.add(txt)
    keywords = soup.find("meta", {"name": "keywords"})
    if keywords and keywords.get("content"):
        for k in keywords["content"].split(","):
            k = k.strip()
            if len(k) < 25:
                tags.add(k)
    return list(tags)[:3]

def scrape_recipes():
    print("🔎 Starting recipe scrape...")
    if not os.path.exists(SITES_FILE):
        print(f"⚠️ Missing sites file: {SITES_FILE}")
        return

    with open(SITES_FILE, "r", encoding="utf-8") as f:
        sites = [line.strip() for line in f if line.strip()]

    all_recipes = []
    for site in sites:
        try:
            response = requests.get(site, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(response.text, "html.parser")
            for a in soup.find_all("a", href=True):
                href = urljoin(site, a["href"])
                if "/recipe/" in href and "allrecipes.com" in href:
                    all_recipes.append(clean_url(href))
        except Exception as e:
            print(f"⚠️ Error reading {site}: {e}")

    all_recipes = list(set(all_recipes))
    print(f"✅ Found {len(all_recipes)} recipe links.")

    existing = ""
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            existing = f.read()

    # Ensure header + <ul> structure exist
    if "<ul>" not in existing:
        print("🧱 Creating new list structure...")
        existing = HEADER + "\n<ul>\n</ul>\n\n[🏠 Back to Home](../index.md)\n"

    new_blocks = []
    added = 0
    for link in all_recipes:
        if link in existing:
            continue
        try:
            r = requests.get(link, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(r.text, "html.parser")
            title_tag = soup.find("meta", property="og:title")
            title = title_tag["content"].strip() if title_tag else soup.title.string.strip()
            img_tag = soup.find("meta", property="og:image")
            img_url = img_tag["content"] if img_tag else FALLBACK_IMG
            tags = extract_tags(soup)
            tag_text = ", ".join(tags) if tags else "Dinner, Easy"
            block = f"""
<li>
  <h3>{title}</h3>
  <img src="{img_url}" alt="{title}">
  <p><a href="{link}">View Recipe</a></p>
  <p><strong>Tags:</strong> {tag_text}</p>
</li>
"""
            new_blocks.append(block)
            added += 1
            if added >= 5:
                break
        except Exception as e:
            print(f"⚠️ Skipped {link}: {e}")

    if not new_blocks:
        print("ℹ️ No new recipes added.")
        return

    # Insert new recipes before </ul>
    updated_content = re.sub(r"</ul>", "\n".join(new_blocks) + "\n</ul>", existing, count=1)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(updated_content)
    print(f"🎉 Added {len(new_blocks)} new recipes and kept list aligned.")

if __name__ == "__main__":
    scrape_recipes()
