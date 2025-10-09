import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
from datetime import datetime
import os

# --- File Paths ---
SITES_FILE = "data/sites.txt"
OUTPUT_FILE = "recipes/weekly_recipes.md"
FALLBACK_IMG = "assets/fallback.png"

# --- Markdown Header Template ---
HEADER = """<link rel="stylesheet" href="../assets/style.css?v=3">

<div class="header">
  <a href="../index.md" class="title">🍴 Recipe Scraper</a>
  <span class="subtitle">Weekly Auto-Generated Dinners</span>
</div>

# 🥘 Weekly Recipes

These recipes are scraped automatically every Monday morning.
Designed for 2–3 servings, they focus on simplicity and great flavor.

---
"""

# --- Helper: Normalize URLs ---
def clean_url(url):
    return url.split("?")[0].rstrip("/")

# --- Helper: Extract recipe tags ---
def extract_tags(soup):
    tags = set()

    # Try AllRecipes-specific tag selectors
    tag_areas = soup.select("a.recipe-category-link, span.mntl-taxonomy-list-item, span.mntl-recipe-taxonomy")
    for t in tag_areas:
        txt = t.get_text(strip=True)
        if txt and len(txt) < 25:
            tags.add(txt)

    # Fallback: search for keywords in meta tags
    keywords = soup.find("meta", {"name": "keywords"})
    if keywords and keywords.get("content"):
        for k in keywords["content"].split(","):
            k = k.strip()
            if len(k) < 25:
                tags.add(k)

    return list(tags)[:3]  # Limit to top 3

# --- Main Scraper ---
def scrape_recipes():
    print("🔎 Starting recipe scrape...")
    with open(SITES_FILE, "r", encoding="utf-8") as f:
        sites = [line.strip() for line in f if line.strip()]

    all_recipes = []

    for site in sites:
        print(f"🧠 Reading site: {site}")
        try:
            response = requests.get(site, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(response.text, "html.parser")

            # Find all recipe links on the page
            for a in soup.find_all("a", href=True):
                href = urljoin(site, a["href"])
                if "/recipe/" in href and "allrecipes.com" in href:
                    all_recipes.append(clean_url(href))
        except Exception as e:
            print(f"⚠️ Error reading {site}: {e}")

    # Deduplicate links
    all_recipes = list(set(all_recipes))
    print(f"✅ Found {len(all_recipes)} total recipe links")

    # --- Load existing file to prevent duplicates ---
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            existing = f.read()
    else:
        existing = ""

    # --- Write header if file is new ---
    new_content = []
    if not existing.strip():
        new_content.append(HEADER)

    # --- Scrape details for up to 5 new recipes ---
    added = 0
    for link in all_recipes:
        if link in existing:
            continue  # skip duplicates
        try:
            r = requests.get(link, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(r.text, "html.parser")

            # Extract title
            title_tag = soup.find("meta", property="og:title")
            title = title_tag["content"].strip() if title_tag else soup.title.string.strip()

            # Extract image
            img_tag = soup.find("meta", property="og:image")
            img_url = img_tag["content"] if img_tag else FALLBACK_IMG

            # Extract tags
            tags = extract_tags(soup)
            tag_text = ", ".join(tags) if tags else "Dinner, Easy"

            # Add formatted Markdown block
            block = f"""
<li>
  <h3>{title}</h3>
  <img src="{img_url}" alt="{title}">
  <p><a href="{link}">View Recipe</a></p>
  <p><strong>Tags:</strong> {tag_text}</p>
</li>
"""
            new_content.append(block)
            added += 1

            print(f"✅ Added: {title}")

            if added >= 5:
                break  # keep list small for weekly update
        except Exception as e:
            print(f"⚠️ Skipped {link} due to error: {e}")

    # --- Write results ---
    if added:
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write("\n".join(new_content))
        print(f"🎉 Added {added} new recipes to {OUTPUT_FILE}")
    else:
        print("ℹ️ No new recipes found this week.")


if __name__ == "__main__":
    scrape_recipes()
