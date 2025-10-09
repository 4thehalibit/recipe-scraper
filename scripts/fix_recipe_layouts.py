import os
import re

RECIPES_PATH = "recipes"

def fix_markdown(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find all <li>...</li> recipe blocks
    recipe_blocks = re.findall(r"<li>.*?</li>", content, re.DOTALL)

    if not recipe_blocks:
        print(f"ℹ️ No recipes found in {file_path}")
        return

    # Deduplicate based on title text inside <h3> tags
    unique_blocks = []
    seen_titles = set()
    for block in recipe_blocks:
        match = re.search(r"<h3>(.*?)</h3>", block)
        title = match.group(1).strip() if match else block[:50]
        if title not in seen_titles:
            seen_titles.add(title)
            unique_blocks.append(block)
        else:
            print(f"🧹 Removed duplicate: {title}")

    # Remove existing <ul>...</ul> sections
    content = re.sub(r"<ul>.*?</ul>", "", content, flags=re.DOTALL)

    # Build a clean <ul> with unique blocks
    ul_block = "<ul>\n" + "\n".join(unique_blocks) + "\n</ul>\n"

    # Preserve header and footer
    parts = content.split("[🏠 Back to Home]")
    header = parts[0].strip()
    footer = "[🏠 Back to Home]" + (parts[1] if len(parts) > 1 else "")

    # Rebuild file
    fixed = f"{header}\n\n{ul_block}\n\n{footer.strip()}\n"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(fixed)

    print(f"✅ Fixed layout for {file_path} ({len(unique_blocks)} unique recipes).")


def main():
    for fname in os.listdir(RECIPES_PATH):
        if fname.endswith(".md"):
            fix_markdown(os.path.join(RECIPES_PATH, fname))


if __name__ == "__main__":
    main()
