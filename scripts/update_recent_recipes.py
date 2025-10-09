import re
from pathlib import Path

WEEKLY = Path("recipes/weekly_recipes.md")
MINE   = Path("recipes/my_recipes.md")
INDEX  = Path("index.md")

def extract_links_from_html(content: str):
    """Find <li>…<h3>Title</h3>…<a href="URL">…</a>…</li> blocks."""
    pairs = []
    # One <li> card: grab title from <h3> and URL from the first anchor inside the card
    for li in re.findall(r"<li>.*?</li>", content, flags=re.DOTALL | re.IGNORECASE):
        h3 = re.search(r"<h3>(.*?)</h3>", li, flags=re.DOTALL | re.IGNORECASE)
        a  = re.search(r'<a\s+href="([^"]+)"[^>]*>.*?</a>', li, flags=re.DOTALL | re.IGNORECASE)
        if h3 and a:
            title = re.sub(r"\s+", " ", h3.group(1)).strip()
            url   = a.group(1).strip()
            pairs.append((title, url))
    return pairs

def extract_links_from_md(content: str):
    """Find - [Title](URL) markdown links (fallback)."""
    return [(t.strip(), u.strip()) for t, u in re.findall(r"- \[(.*?)\]\((.*?)\)", content)]

def read_links(path: Path):
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    links = extract_links_from_html(text)
    # Also include any markdown-style links if present
    links += extract_links_from_md(text)
    return links

def build_recent_list(max_items=3):
    weekly_links = read_links(WEEKLY)
    my_links     = read_links(MINE)

    # Combine in the order they appear in files (older first).
    combined = weekly_links + my_links

    # Take the most recent UNIQUE by URL (last occurrence wins), then keep last N
    seen = set()
    recent = []
    for title, url in reversed(combined):
        if url not in seen:
            recent.append((title, url))
            seen.add(url)
        if len(recent) >= max_items:
            break
    recent.reverse()
    return recent

def update_index(latest):
    if not INDEX.exists():
        print("⚠️ index.md not found.")
        return
    idx = INDEX.read_text(encoding="utf-8")

    # Build replacement block (HTML links for consistency)
    recent_html = "\n".join([f'- <a href="{u}" target="_blank">{t}</a>' for t, u in latest])
    new_block = f"## 🆕 Recently Added\n\n{recent_html}\n"

    # First try: replace an existing Recently Added section (between header and next header or EOF)
    pattern = r"## 🆕 Recently Added[\s\S]*?(?=\n## |\Z)"
    if re.search(pattern, idx):
        idx = re.sub(pattern, new_block, idx)
    else:
        # Try to replace a placeholder div (if you had one)
        placeholder = r'<div id="recent-recipes">[\s\S]*?</div>'
        if re.search(placeholder, idx):
            idx = re.sub(placeholder, f"\n{new_block}\n", idx)
        else:
            # Fallback: append the section before the footer or at the end
            if "</footer>" in idx:
                idx = idx.replace("</footer>", f"\n{new_block}\n</footer>")
            else:
                idx = idx.rstrip() + "\n\n" + new_block + "\n"

    INDEX.write_text(idx, encoding="utf-8")
    print(f"✅ Recently Added updated with {len(latest)} item(s).")

def main():
    latest = build_recent_list(max_items=3)
    if not latest:
        print("ℹ️ No recipes found in weekly or personal lists. Skipping.")
        return
    update_index(latest)

if __name__ == "__main__":
    main()
