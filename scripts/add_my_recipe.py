import sys
import re
import requests
from bs4 import BeautifulSoup
from datetime import date

def get_recipe_info(url):
    """Extract title, image, and tags from a recipe link"""
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print(f"❌ Failed to fetch URL: {e}")
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

    return {
        "title": title,
        "image": image,
        "tags": tags,
        "url": url,
    }


def append_to_my_recipes(recipe):
    """Add the scraped recipe info into my_recipes.md"""
    section = (
        f"## {recipe['title']}\n"
        + (f"![{recipe['title']}]({recipe['image']})\n" if recipe["image"] else "")
        + f"- [View Recipe]({recipe['url']})\n"
        + (f"- Tags: {', '.join(recipe['tags'])}\n" if recipe["tags"] else "")
        + f"- Added: {date.today():%B %d, %Y}\n"
        + "- Notes: \n\n"
        + "---\n\n"
    )

    with open("my_recipes.md", "a", encoding="utf-8") as f:
        f.write(section)

    print(f"✅ Added '{recipe['title']}' to my_recipes.md")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python add_my_recipe.py <recipe_url>")
        sys.exit(1)

    url = sys.argv[1]
    recipe = get_recipe_info(url)
    if recipe:
        append_to_my_recipes(recipe)
