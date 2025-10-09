import os
import re

RECIPES_PATH = "recipes"

def fix_markdown(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # --- Extract all <li> blocks, ignoring spacing or stray markup
    recipe_blocks = re.findall(r"<li>\s*?<h3>.*?</li>", content, re.DOTALL | re.IGNORECASE)
    if not recipe_blocks:
        print(f"ℹ️ No recipes found in {file_path}")
        return

    # --- Deduplicate by recipe title
    unique_blocks = []
    seen_titles = set()
    for block in recipe_blocks:
        m = re.search(r"<h3>(.*?)</h3>", block, re.DOTALL)
        title = re.sub(r"\s+", " ", m.group(1)).strip() if m else block[:40]
        if title.lower() not in seen_titles:
            seen_titles.add(title.lower())
            unique_blocks.append(block)
        else:
            print(f"🧹 Removed duplicate: {title}")

    # --- Remove all old lists completely (inside or outside)
    content = re.sub(r"<ul>.*?</ul>", "", content, flags=re.DOTALL | re.IGNORECASE)

    # --- Build clean UL with unique recipes
    new_list = "<ul>\n" + "\n".join(unique_blocks) + "\n</ul>\n"

    # --- Preserve header and footer
    parts = content.split("[🏠 Back to Home]")
    header = parts[0].strip()
    footer = "[🏠 Back to Home]" + (parts[1] if len(parts) > 1 else "")

    fixed = f"{header}\n\n{new_list}\n\n{footer.strip()}\n"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(fixed)

    print(f"✅ Cleaned {file_path}: {len(unique_blocks)} unique recipes retained.")


def main():
    for fname in os.listdir(RECIPES_PATH):
        if fname.endswith(".md"):
            fix_markdown(os.path.join(RECIPES_PATH, fname))


if __name__ == "__main__":
    main()
