import requests
from bs4 import BeautifulSoup
import os
import re

LINK_FILE = "data/my_recipe_links.txt"
OUTPUT_FILE = "recipes/my_recipes.md"
FALLBACK_IMG = "assets/fallback.png"

HEADER = """<link rel="stylesheet" href="../assets/style.css?v=3">

<div class="header">
  <a href="../index.md" class="title">🍴 Recipe Scraper</a>
  <span class="subtitle">My Saved Favorites</span>
</div>

# 👨‍🍳 My Recipes

Below are my saved favorites and personally added recipes.
Each time I paste links into `data/my_recipe_links.txt`, this list updates automatically.

---
"""

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

def get_recipe_info(url):
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        title_tag = soup.find("meta", property="og:title")
        title = title_tag["content"].strip() if title_tag else (soup.title.string.strip() if soup.title else "Untitled Recipe")
        img_tag = soup.find("meta", property="og:image")
        img_url = img_tag["content"] if img_tag else FALLBACK_IMG
        tags = extract_tags(soup)
        tag_text = ", ".join(tags) if tags else "Dinner, Favorite"
        block = f"""
<li>
  <h3>{title}</h3>
  <img src="{img_url}" alt="{title}">
  <p><a href="{url}">View Recipe</a></p>
  <p><strong>Tags:</strong> {tag_text}</p>
</li>
"""
        return block
    except Exception as e:
        print(f"⚠️ Failed to fetch {url}: {e}")
        return None

def main():
    if not os.path.exists(LINK_FILE):
        print(f"⚠️ No link file found: {LINK_FILE}")
        return
    with open(LINK_FILE, "r", encoding="utf-8") as f:
        links = [line.strip() for line in f if line.strip()]
    if not links:
        print("ℹ️ No new links found.")
        return

    existing = ""
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            existing = f.read()

    # Create header + <ul> if missing
    if "<ul>" not in existing:
        print("🧱 Creating new list structure...")
        existing = HEADER + "\n<ul>\n</ul>\n\n[🏠 Back to Home](../index.md)\n"

    # Collect new blocks
    new_blocks = []
    for url in links:
        if url in existing:
            print(f"⏭️ Skipping duplicate: {url}")
            continue
        block = get_recipe_info(url)
        if block:
            new_blocks.append(block)
            print(f"✅ Added: {url}")

    if not new_blocks:
        print("ℹ️ No new recipes added.")
        return

    # Insert before </ul>
    updated_content = re.sub(r"</ul>", "\n".join(new_blocks) + "\n</ul>", existing, count=1)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print(f"🎉 Added {len(new_blocks)} new recipes and kept layout aligned.")

    # Clear input file
    with open(LINK_FILE, "w", encoding="utf-8") as f:
        f.write("")

if __name__ == "__main__":
    main()
