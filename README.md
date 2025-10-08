# 🍳 Recipe Scraper

This GitHub Action scrapes **easy recipes for 2–3 people** from multiple websites and updates a Markdown list every Monday morning.

---

## 🧰 How It Works

- Runs automatically every Monday at **8 AM Central (13:00 UTC)**
- Scrapes recipe links and titles from every site listed in `sites.txt`
- Appends a new section in `weekly_recipes.md` labeled with the current week
- Commits results automatically to the repository

---

## 🗂️ Repository Structure

```
recipe-scraper/
├── .github/
│   └── workflows/
│       └── recipe.yml        # GitHub Action workflow (runs weekly)
├── scraper.py                # Python script that performs the scraping
├── sites.txt                 # List of recipe search URLs
├── requirements.txt          # Python dependencies
└── weekly_recipes.md         # Auto-generated output file
```

---

## 🔗 Adding or Removing Recipe Sources

You can add new recipe sites by editing `sites.txt` — **one URL per line**.  
No code changes are required.

Example:

```
https://www.allrecipes.com/search?q=easy+dinner+for+2
https://www.bbcgoodfood.com/search/recipes?q=easy+dinner+for+3
https://www.eatingwell.com/search/?q=easy+dinner+for+2
https://www.tasty.co/search?q=easy+dinner+for+two
```

When the workflow runs next (or you trigger it manually), all URLs in this file will be scraped.

---

## 🕒 Running the Workflow

The scraper runs automatically each Monday, but you can also trigger it manually:

1. Go to the **Actions** tab in your repository.
2. Click **Weekly Recipe Scraper**.
3. Click **Run workflow → Run workflow**.

---

## 🧾 Output Example

Each run adds a dated section to `weekly_recipes.md`:

```
## Week of October 7, 2025

_Automatically updated every Monday_

- [Easy Shrimp Dinner](https://www.allrecipes.com/recipe/20450/easy-shrimp-dinner/)
- [Quick and Easy Stuffed Peppers](https://www.allrecipes.com/recipe/14044/quick-and-easy-stuffed-peppers/)
- [Creamy Chicken Pasta](https://www.bbcgoodfood.com/creamy-chicken-pasta)
```

---

## ⚙️ Manual Testing Locally

If you want to test it on your own machine:

```bash
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scraper.py
```

This will update or create `weekly_recipes.md` locally.

---

## 🧠 Notes

- Each Monday’s run adds a new dated section instead of overwriting old content.
- The number of results is limited to 30 per run (adjustable in `scraper.py`).
- Adding or removing URLs in `sites.txt` is safe — the next workflow run will handle them automatically.

---

Happy cooking and coding! 🍽️
