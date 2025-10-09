import re
import requests
from bs4 import BeautifulSoup
from datetime import date
import os
import random

# =============== CONFIG ===============
SITES_FILE = "data/sites.txt"
WEEKLY_FILE = "recipes/weekly_recipes.md"
MY_RECIPES_FILE = "recipes/my_recipes.md"
MAX_RECIPES = 5               # slow-growing list
TOC_HEADER = "## 📖 Table of Contents"
# =====================================


def load_sites():
    """Load recipe source URLs from sites.txt"""
    with open(SITES_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def get_tags_and_image(recipe_url):
    """Extract tags and main image from a recipe page"""
    try:
        r = requests.get(recipe_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
    except Exception:
        return [], None

    soup = BeautifulSoup(r.text, "html.parser")

    # Tags
    tags = []
    for tag in soup.select("a[href*='/recipes/'], a[href*='/tag/'], a[class*='taxonomy'], a[class*='link']"):
        t = tag.get_text(strip=True)
        if len(t) > 2 and t.lower() not in ("home", "recipes", "login", "sign up"):
            tags.append(t)
    tags = list(set(tags))[:5]

    # Image
    img_tag = soup.find("meta", property="og:image")
    image = img_tag["content"] if img_tag and img_tag.get("content") else None

    return tags, image


def load_existing_recipes():
    """Read existing recipes to prevent duplicates"""
    seen_links = set()
    seen_titles = set()
    if not os.path.exists(WEEKLY_FILE):
        return seen_links, seen_titles

    with open(WEEKLY_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    for match in re.finditer(r"\[([^\]]+)\]\((https?://[^\)]+)\)", content):
        title = match.group(1).strip().lower()
        link = match.group(2).strip().lower()
        seen_links.add(link)
        seen_titles.add(re.sub(r"[^a-z0-9]+", "", title))
    return seen_links, seen_titles


def scrape_recipes(sites, seen_links, seen_titles):
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
            title_clean = re.sub(r'\d+\s*(Ratings|Reviews)?$', '', title).strip()
            href = link.get("href")

            if not title_clean or not href or not href.startswith("http"):
                continue

            title_key = re.sub(r"[^a-z0-9]+", "", title_clean.lower())
            if href.lower() in seen_links or title_key in seen_titles:
                continue

            tags, image = get_tags_and_image(href)
            recipe_md = f"### {title_clean}\n"
            if image:
                recipe_md += f"![{title_clean}]({image})\n"
            recipe_md += f"- [View Recipe]({href})\n"
            if tags:
                recipe_md += f"- Tags: {', '.join(tags)}\n"

            recipes.append(recipe_md + "\n")
            seen_links.add(href.lower())
            seen_titles.add(title_key)

    return recipes


def generate_toc():
    """Generate Table of Contents from all weekly sections"""
    with open(WEEKLY_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    weeks = [line.strip() for line in lines if line.startswith("## Week of")]
    toc = [f"{TOC_HEADER}\n"] + [
        f"- [{w}](#{w.lower().replace(' ', '-').replace(',', '')})\n" for w in weeks
    ]

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

    with open(WEEKLY_FILE, "w", encoding="utf-8") as f:
        f.write("# 🍳 Easy Recipes for 2–3 People\n\n")
        f.write("_Automatically updated every Monday_\n\n")
        f.write("---\n\n")
        f.writelines(toc)
        f.write("\n---\n\n")
        f.writelines(content)


if __name__ == "__main__":
    sites = load_sites()
    seen_links, seen_titles = load_existing_recipes()
    recipes = scrape_recipes(sites, seen_links, seen_titles)

    if not recipes:
        print("ℹ️ No new unique recipes found this week.")
    else:
        recipes = random.sample(recipes, min(len(recipes), MAX_RECIPES))
        with open(WEEKLY_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n\n## Week of {date.today():%B %d, %Y}\n\n")
            for recipe in recipes:
                f.write(recipe)

        generate_toc()
        print(f"✅ Added {len(recipes)} new recipes to {WEEKLY_FILE}.")
