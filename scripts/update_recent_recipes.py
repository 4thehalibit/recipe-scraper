import re
from pathlib import Path

# Paths
weekly_file = Path("recipes/weekly_recipes.md")
my_file = Path("recipes/my_recipes.md")
index_file = Path("index.md")

def extract_links(file: Path):
    """Extracts recipe titles and URLs from either HTML or Markdown list items."""
    if not file.exists():
        return []
    content = file.read_text(encoding="utf-8")

    # Match both HTML and Markdown-style links
    html_links = re.findall(r'<a href="(.*?)">(.*?)</a>', content)
    md_links = re.findall(r"- \[(.*?)\]\((.*?)\)", content)

    # Normalize as (title, url)
    links = [(title.strip(), url.strip()) for url, title in html_links]
    links += [(title.strip(), url.strip()) for title, url in md_links]

    return links

# Gather all links
weekly_links = extract_links(weekly_file)
my_links = extract_links(my_file)

# Combine and deduplicate
all_links = weekly_links + my_links
seen = set()
unique_links = []
for title, url in all_links:
    if url not in seen:
        unique_links.append((title, url))
        seen.add(url)

# Take up to 3 latest
latest = unique_links[:3]

if not latest:
    print("⚠️ No recipes found in either file.")
    exit(0)

# Build HTML output
recent_html = "\n".join(
    [f'- <a href="{url}" target="_blank">{title}</a>' for title, url in latest]
)
replacement = f"""
## 🆕 Recently Added

{recent_html}
"""

# Update index.md
index_content = index_file.read_text(encoding="utf-8")

new_content = re.sub(
    r"## 🆕 Recently Added[\s\S]*?(?=\Z|## )",
    replacement.strip(),
    index_content,
)

index_file.write_text(new_content, encoding="utf-8")

print(f"✅ Recently Added updated with {len(latest)} recipe(s).")
