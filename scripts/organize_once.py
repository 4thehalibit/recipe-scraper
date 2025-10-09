import os
import shutil

# Define the desired folder layout
folders = [
    "data",
    "recipes",
    "scripts",
    "docs",
    ".github/workflows",
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)

moves = {
    "sites.txt": "data/sites.txt",
    "my_recipe_links.txt": "data/my_recipe_links.txt",
    "weekly_recipes.md": "recipes/weekly_recipes.md",
    "my_recipes.md": "recipes/my_recipes.md",
    "scraper.py": "scripts/scraper.py",
    "add_my_recipe.py": "scripts/add_my_recipe.py",
    "requirements.txt": "scripts/requirements.txt",
    "README.md": "docs/README.md",
    "recipe.yml": ".github/workflows/recipe.yml",
}

for src, dst in moves.items():
    if os.path.exists(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        print(f"📦 Moving {src} → {dst}")
        shutil.move(src, dst)

print("\n✅ One-time organization complete.")
print("   All folders created and files moved into place.")
