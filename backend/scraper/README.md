# Recipe Scraper Tools

## 📊 Current Database: 228 Recipes

### By Source:
- **TheMealDB**: 199 recipes (free API, no key needed)
- **Curated**: 21 recipes (manually added)
- **Bootstrap**: 8 recipes (starter recipes)

### By Cuisine (Top 10):
- Spanish: 20 | American: 19 | British: 18 | Italian: 17
- Turkish: 15 | French: 14 | Chinese: 9 | Indian: 8
- Algerian: 7 | Vietnamese: 7

### By Category:
- Main dishes: 163 | Sides: 20 | Desserts: 19 
- Breakfast: 16 | Appetizers: 5 | Salads: 3 | Soups: 2

---

## 🚀 Available Tools

### 1. **API Recipe Importer** (RECOMMENDED)
Imports from free recipe APIs with no account needed.

```bash
# TheMealDB - 300+ recipes (NO API KEY NEEDED!)
python scraper/api_recipe_importer.py --source themealdb --limit 300

# Recipe Puppy - 1M+ recipes (NO API KEY NEEDED!)
python scraper/api_recipe_importer.py --source recipepuppy --limit 1000

# Both sources
python scraper/api_recipe_importer.py --source all --limit 2000
```

**Features:**
- ✅ No API keys required
- ✅ Smart duplicate detection
- ✅ Progress tracking
- ✅ Legal compliance (facts only + AI rewriting)
- ✅ Works offline after import

---

### 2. **Bootstrap Recipes**
Adds curated, hand-picked popular recipes.

```bash
python scraper/simple_recipe_bootstrap.py
```

Currently includes 10 recipes. Edit the file to add more manually.

---

### 3. **Legal Recipe Importer**
Low-level tool for importing from custom sources.

```bash
python scraper/legal_recipe_importer.py
```

Used internally by other scrapers. Ensures legal compliance by:
- Extracting only facts (ingredients, times, steps)
- Generating original descriptions
- Adding proper attribution

---

## 📈 Growth Strategy

### Current: 228 recipes ✅
TheMealDB has been very successful!

### Goal: 500 recipes
```bash
# Fetch remaining TheMealDB recipes
python scraper/api_recipe_importer.py --source themealdb --limit 300
```

### Goal: 1,000+ recipes
```bash
# Add Recipe Puppy (if API is back online)
python scraper/api_recipe_importer.py --source recipepuppy --limit 800

# Or add more curated recipes via bootstrap
# Edit simple_recipe_bootstrap.py and add 500+ recipes manually
```

### Goal: 5,000+ recipes
Options:
1. **Edamam API** (free tier, requires key - 10k recipes/month)
2. **Spoonacular API** (free tier, requires key - 150 requests/day)
3. **Combine multiple free APIs**

---

## 🛡️ Legal & Ethical

All scrapers follow legal best practices:
1. ✅ Only extract **facts** (not copyrightable)
2. ✅ Generate **original descriptions** (transformative use)
3. ✅ Add **source attribution**
4. ✅ Respect **rate limits** (1-2 sec delays)
5. ✅ Use **free public APIs** (within terms of service)

See `../LEGAL_RECIPE_GUIDE.md` for full details.

---

## 🔧 Troubleshooting

### "Recipe Puppy API not working"
- The API sometimes goes down
- Try again later or use TheMealDB only

### "Rate limit exceeded"
- Add longer delays between requests
- Use `--use-ai` flag with caution (Groq free tier: 30 req/min)

### "Too many duplicates"
- Normal! The duplicate detection is working
- APIs sometimes return similar recipes with different names

### "Want more recipes faster?"
- Run multiple imports from different sources
- Edit `api_recipe_importer.py` to add more API sources
- Manually add recipes via `simple_recipe_bootstrap.py`

---

## 📝 Adding New API Sources

To add a new recipe API:

1. Create a `fetch_APINAME` method in `api_recipe_importer.py`
2. Create a `_parse_APINAME_recipe` method to convert to our format
3. Add to the `import_recipes` method
4. Test with `--limit 10` first

Example API sources to consider:
- **TheMealDB** ✅ (implemented)
- **Recipe Puppy** ✅ (implemented, but currently down)
- **Edamam** (requires free API key)
- **Spoonacular** (requires free API key)
- **Tasty API** (unofficial)

---

## 🎯 Next Steps

1. **Get to 300 recipes**: Run TheMealDB import again
2. **Test the app**: Make sure Quick/Explore features work well
3. **Gather feedback**: See what cuisines/categories users want
4. **Expand strategically**: Add APIs for missing cuisines

---

**Questions?** Check `../LEGAL_RECIPE_GUIDE.md` or just run the commands! 🚀

