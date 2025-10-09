import re
from pathlib import Path

# Paths
weekly_file = Path("recipes/weekly_recipes.md")
my_file = Path("recipes/my_recipes.md")
index_file = Path("index.md")

# Function to extract recipes from a file
def extract_links(file: Path):
    if not file.exists():
        return []
    content = file.read_text(encoding="utf-8")
    return re.findall(r"- \[(.*?)\]\((.*?)\)", content)

# Collect recent recipes from both lists
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

# Get the first 3 (most recent)
latest = unique_links[:3]

if not latest:
    print("⚠️ No recipes found in either list.")
    exit(0)

# Build HTML snippet
recent_html = "\n".join(
    [f'- <a href="{url}" target="_blank">{title}</a>' for title, url in latest]
)
replacement = f"""
## 🆕 Recently Added

{recent_html}
"""

# Update the homepage
index_content = index_file.read_text(encoding="utf-8")

new_content = re.sub(
    r"## 🆕 Recently Added[\s\S]*?(?=\Z|## )",
    replacement.strip(),
    index_content,
)

index_file.write_text(new_content, encoding="utf-8")

print("✅ Recently Added section updated with latest personal + weekly recipes!")
