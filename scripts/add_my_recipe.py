import re
import requests
from bs4 import BeautifulSoup
from datetime import date
import os
import time

LINK_FILE = "data/my_recipe_links.txt"
MY_RECIPES_FILE = "recipes/my_recipes.md"


def get_recipe_info(url):
    """Extract title, image, and tags from a recipe page"""
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print(f"❌ Failed to fetch {url}: {e}")
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    # Title
    title_tag = soup.find("meta", property="og:title") or soup.find("title")
    title = title_tag.get("content") if title_tag and title_tag.get("content") else title_tag.text
    title = title.strip().replace("| Allrecipes", "").replace("BBC Good Food", "").strip()

    # Image
    img_tag = soup.find("meta", property="og:image")
    image = img_tag["content"] if img_tag and img_tag.get("content") else None

    # Tags
    tags = []
    for tag in soup.select("a[href*='/recipes/'], a[href*='/tag/'], a[class*='taxonomy'], a[class*='link']"):
        t = tag.get_text(strip=True)
        if len(t) > 2 and t.lower() not in ("home", "recipes", "login", "sign up"):
            tags.append(t)
    tags = list(set(tags))[:5]

    return {"title": title, "image": image, "tags": tags, "url": url}


def load_existing_links():
    """Read existing links from my_recipes.md to avoid duplicates"""
    seen_links = set()
    if not os.path.exists(MY_RECIPES_FILE):
        return seen_links

    with open(MY_RECIPES_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    for match in re.finditer(r"\((https?://[^\)]+)\)", content):
        seen_links.add(match.group(1).strip().lower())
    return seen_links


def append_to_my_recipes(recipe):
    """Add a new entry to my_recipes.md"""
    section = (
        f"## {recipe['title']}\n"
        + (f"![{recipe['title']}]({recipe['image']})\n" if recipe["image"] else "")
        + f"- [View Recipe]({recipe['url']})\n"
        + (f"- Tags: {', '.join(recipe['tags'])}\n" if recipe["tags"] else "")
        + f"- Added: {date.today():%B %d, %Y}\n"
        + "- Notes: \n\n"
        + "---\n\n"
    )
    with open(MY_RECIPES_FILE, "a", encoding="utf-8") as f:
        f.write(section)
    print(f"✅ Added '{recipe['title']}'")


def process_link_file():
    """Scan my_recipe_links.txt and import new recipes"""
    if not os.path.exists(LINK_FILE):
        print(f"⚠️ No {LINK_FILE} found.")
        return

    with open(LINK_FILE, "r", encoding="utf-8") as f:
        urls = [u.strip() for u in f if u.strip()]

    if not urls:
        print("ℹ️ No URLs in my_recipe_links.txt.")
        return

    seen_links = load_existing_links()
    new_urls = [u for u in urls if u.lower() not in seen_links]

    if not new_urls:
        print("ℹ️ All URLs already imported.")
        return

    print(f"🧾 Found {len(new_urls)} new recipe(s) to import...\n")

    for url in new_urls:
        recipe = get_recipe_info(url)
        if recipe:
            append_to_my_recipes(recipe)
            time.sleep(1)

    # Remove processed links
    remaining = [u for u in urls if u.lower() not in new_urls]
    with open(LINK_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(remaining))

    print(f"\n🍽️ Imported {len(new_urls)} recipe(s) into {MY_RECIPES_FILE}.")


if __name__ == "__main__":
    process_link_file()
