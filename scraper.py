import re
import requests
from bs4 import BeautifulSoup

url = "https://www.allrecipes.com/search?q=easy+dinner+for+2"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(r.text, "html.parser")

recipes = []
for link in soup.select("a[href*='/recipe/']")[:10]:
    title = link.get_text(strip=True)

    # Remove anything like '43Ratings', '43', or '43 Reviews' at the end
    title = re.sub(r'\d+\s*(Ratings|Reviews)?$', '', title).strip()

    href = link.get("href")
    if title and href and "allrecipes.com/recipe/" in href:
        recipes.append(f"- [{title}]({href})")

with open("weekly_recipes.md", "w", encoding="utf-8") as f:
    f.write("# 🍳 Easy Recipes for 2–3 People\n\n")
    f.write("\n".join(recipes))
