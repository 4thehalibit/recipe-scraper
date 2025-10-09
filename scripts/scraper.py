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

    return list(tags)[:3]  # Limit to top 3


# --- Helper: Refresh missing or fallback images ---
def refresh_existing_images():
    if not os.path.exists(OUTPUT_FILE):
        return

    print("♻️ Checking for recipes with missing or fallback images...")
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    matches = re.findall(r'<img src="assets/fallback\.png" alt="([^"]+)"', content)
    updated_count = 0

    for title in matches:
        print(f"🔄 Refreshing image for: {title}")
        search_url = f"https://www.allrecipes.com/search?q={title.replace(' ', '+')}"
        try:
            r = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            img_tag = soup.find("meta", property="og:image")
            if img_tag:
                new_img = img_tag["content"]
                content = content.replace(
                    f'<img src="assets/fallback.png" alt="{title}">',
                    f'<img src="{new_img}" alt="{title}">'
                )
                updated_count += 1
                print(f"✅ Updated image for {title}")
        except Exception as e:
            print(f"⚠️ Failed to update {title}: {e}")

    if updated_count > 0:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"🎉 Refreshed {updated_count} existing fallback images!")
    else:
        print("ℹ️ No fallback images found to refresh.")


# --- Main Scraper ---
def scrape_recipes():
    print("🔎 Starting recipe scrape...")
    if not os.path.exists(SITES_FILE):
        print(f"⚠️ Missing sites file: {SITES_FILE}")
        return

    with open(SITES_FILE, "r", encoding="utf-8") as f:
        sites = [line.strip() for line in f if line.strip()]

    all_recipes = []

    for site in sites:
        print(f"🧠 Reading site: {site}")
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
    print(f"✅ Found {len(all_recipes)} potential recipe links")

    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            existing = f.read()
    else:
        existing = ""

    new_content = []
    if not existing.strip():
        new_content.append(HEADER)

    added = 0
    for link in all_recipes:
        if link in existing:
            continue  # skip duplicates

        try:
            r = requests.get(link, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(r.text, "html.parser")

            title_tag = soup.find("meta", property="og:title")
            title = title_tag["content"].strip() if title_tag else (soup.title.string.strip() if soup.title else "Untitled Recipe")

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
            new_content.append(block)
            added += 1

            print(f"✅ Added: {title}")

            if added >= 5:
                break  # Only 5 per week
        except Exception as e:
            print(f"⚠️ Skipped {link}: {e}")

    if added:
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write("\n".join(new_content))
        print(f"🎉 Added {added} new recipes to {OUTPUT_FILE}")
    else:
        print("ℹ️ No new recipes found this week.")


if __name__ == "__main__":
    refresh_existing_images()
    scrape_recipes()
