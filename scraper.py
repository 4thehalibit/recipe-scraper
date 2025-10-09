import re
import requests
from bs4 import BeautifulSoup
from datetime import date
import os

# =============== CONFIG ===============
TOC_HEADER = "## 📖 Table of Contents"
MAX_RECIPES = 25
# =====================================


def load_sites():
    """Load site URLs from sites.txt"""
    with open("sites.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def get_tags_and_image(recipe_url):
    """Extract tags and main image from recipe page"""
    try:
        r = requests.get(recipe_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
    except Exception:
        return [], None

    soup = BeautifulSoup(r.text, "html.parser")

    # --- Tags ---
    tags = []
    for tag in soup.select("a[href*='/recipes/'], a[href*='/tag/'], a[class*='taxonomy'], a[class*='link']"):
        t = tag.get_text(strip=True)
        if len(t) > 2 and t.lower() not in ("home", "recipes", "login", "sign up"):
            tags.append(t)
    tags = list(set(tags))[:5]  # limit to 5 tags

    # --- Image ---
    img_tag = soup.find("meta", property="og:image")
    image = img_tag["content"] if img_tag and img_tag.get("content") else None

    return tags, image


def scrape_recipes(sites):
    """Scrape recipe titles, links, tags, and images"""
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

            if not title or not href or not href.startswith("http"):
                continue

            tags, image = get_tags_and_image(href)
            recipe_md = f"### {title}\n"
            if image:
                recipe_md += f"![{title}]({image})\n"
            recipe_md += f"- [View Recipe]({href})\n"
            if tags:
                recipe_md += f"- Tags: {', '.join(tags)}\n"
            recipes.append(recipe_md + "\n")
    return recipes


def generate_toc(file_path="weekly_recipes.md"):
    """Generate a Table of Contents from all week headers"""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    weeks = [line.strip() for line in lines if line.startswith("## Week of")]
    toc = [f"{TOC_HEADER}\n"] + [
        f"- [{w}](#{w.lower().replace(' ', '-').replace(',', '')})\n" for w in weeks
    ]

    # Remove old TOC
    content = []
    in_toc = False
    for line in lines:
        if line.startswith(TOC_HEADER):
            in_toc = True
            continue
        if in_toc and line.strip() == "---":
            in_toc = False
            continue
        if not in_toc:
            content.append(line)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("# 🍳 Easy Recipes for 2–3 People\n\n")
        f.write("_Automatically updated every Monday_\n\n")
        f.write("---\n\n")
        f.writelines(toc)
        f.write("\n---\n\n")
        f.writelines(content)


if __name__ == "__main__":
    sites = load_sites()
    recipes = scrape_recipes(sites)

    file_path = "weekly_recipes.md"
    is_new_file = not os.path.exists(file_path)

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"\n\n## Week of {date.today():%B %d, %Y}\n\n")
        for recipe in recipes[:MAX_RECIPES]:
            f.write(recipe)

    # Only generate TOC after content exists
    if os.path.exists(file_path):
        generate_toc(file_path)

    print("✅ Weekly recipes updated successfully.")
