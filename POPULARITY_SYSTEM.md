# 🔥 Real-World Popularity Scoring System

## Overview

This system replaces the simple heuristic-based popularity scores with **real-world data** from:
- Google Trends (search interest)
- Recipe platforms (ratings, reviews, saves)
- Recipe quality metrics
- Trending topics

---

## Current System (Simple Heuristic)

**What it does:**
- ✅ Based on recipe metadata (source, completeness, time)
- ❌ NOT based on real popularity data
- ❌ Hardcoded assumptions (e.g., "TheMealDB = 35 points")

**Score components:**
```
Score = Source Quality (40%) + Completeness (30%) + Time (15%) + Ingredients (15%)
```

**Problems:**
- Doesn't reflect what people actually cook
- All recipes from same source get similar scores
- Ignores trending/seasonal recipes
- No real-world validation

---

## New System (Real-World Data)

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    POPULARITY SCORING ENGINE                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. FOOD ALIAS DATABASE (30k+ foods)                        │
│     ├── Normalize recipe names                              │
│     ├── Handle variations ("pad thai" = "phad thai")        │
│     └── Group similar dishes                                │
│                                                               │
│  2. GOOGLE TRENDS API                                        │
│     ├── 90-day trend (current buzz)                         │
│     ├── 5-year baseline (long-term popularity)              │
│     └── Geographic breakdown (optional)                      │
│                                                               │
│  3. PLATFORM ENGAGEMENT                                      │
│     ├── AllRecipes: ratings + reviews                       │
│     ├── Food.com: saves + favorites                         │
│     ├── TheMealDB: view counts                              │
│     └── Reddit: upvotes on r/recipes                        │
│                                                               │
│  4. RECIPE QUALITY (from metadata)                           │
│     ├── Has images, descriptions, tags                      │
│     ├── Detailed instructions                               │
│     └── Reasonable ingredient count                         │
│                                                               │
│  5. RECENCY BOOST                                            │
│     ├── Seasonal trends (pumpkin in fall)                   │
│     ├── Holiday recipes (Christmas, Thanksgiving)           │
│     └── Viral TikTok/Instagram recipes                      │
│                                                               │
└─────────────────────────────────────────────────────────────┘

FINAL SCORE = 
  Google Trends (40%) +
  Platform Engagement (30%) +
  Recipe Quality (20%) +
  Recency Boost (10%)
```

---

## Implementation Steps

### Step 1: Install Dependencies

```bash
cd backend
source venv/bin/activate
pip install pytrends requests requests-cache
```

### Step 2: Set Up Google Trends

```python
# No API key needed for pytrends!
# It uses Google's public Trends interface
from pytrends.request import TrendReq

pytrends = TrendReq(hl='en-US', tz=360)
```

**Rate limits:**
- ~30-50 requests/minute
- Use delays between requests
- Cache results for 7 days

### Step 3: Set Up Platform APIs

#### AllRecipes API
```bash
# AllRecipes doesn't have official API
# Options:
# 1. Web scraping (respectful, with delays)
# 2. Use RapidAPI's Recipe API
# 3. Manual data collection
```

#### Food.com Dataset
```bash
# Use the Kaggle dataset we already have
# It includes ratings and review counts
```

#### TheMealDB API
```bash
# Already using this!
# Has view counts and ratings
```

### Step 4: Build Food Alias Database

**Goal:** Map 30,000+ foods to canonical names

```json
{
  "pad thai": [
    "thai noodles",
    "phad thai",
    "phat thai",
    "ผัดไทย"
  ],
  "fried rice": [
    "chinese fried rice",
    "egg fried rice",
    "yangzhou fried rice"
  ]
}
```

**Sources:**
- USDA Food Database (~8,000 items)
- Wikidata food items (~20,000 items)
- Recipe aggregators (Food.com, AllRecipes)
- Manual curation for common dishes

### Step 5: Run Initial Scoring

```bash
cd backend
python scraper/real_popularity_system.py
```

**Estimated time:**
- 225 recipes × 2 API calls (90d + 5y) = 450 calls
- At 1 call/second = ~8 minutes
- With delays + retries = ~20-30 minutes

### Step 6: Automate Updates

#### Weekly Cron Job
```bash
# Update popularity scores every Sunday at 3 AM
0 3 * * 0 cd /path/to/MyFridge/backend && source venv/bin/activate && python scraper/real_popularity_system.py --auto
```

#### Monthly Full Refresh
```bash
# Full recalculation with platform data updates
0 3 1 * * cd /path/to/MyFridge/backend && source venv/bin/activate && python scraper/real_popularity_system.py --full-refresh
```

---

## Data Sources & APIs

### 1. Google Trends (FREE)

**Setup:**
```python
pip install pytrends
```

**Usage:**
```python
from pytrends.request import TrendReq

pytrends = TrendReq()
pytrends.build_payload(['pad thai'], timeframe='today 3-m')
data = pytrends.interest_over_time()
```

**Pros:**
- ✅ Free, no API key needed
- ✅ Accurate global interest data
- ✅ Seasonal trends

**Cons:**
- ❌ Rate limited (~50/min)
- ❌ No granular recipe-level data

**Docs:** https://pypi.org/project/pytrends/

---

### 2. Recipe Platform APIs

#### Option A: TheMealDB (Already using!)
```bash
API: https://www.themealdb.com/api.php
Free tier: 100 calls/day
```

#### Option B: Spoonacular API
```bash
API: https://spoonacular.com/food-api
Free tier: 150 calls/day
Paid: $0.004/call
```

#### Option C: Edamam Recipe API
```bash
API: https://developer.edamam.com/
Free tier: 10,000 calls/month
```

#### Option D: Web Scraping (respectful)
```python
# AllRecipes, Food Network, Bon Appétit
# Use requests-cache + delays
```

---

### 3. Food Databases

#### USDA FoodData Central (FREE)
- 380,000+ food items
- Nutritional data
- https://fdc.nal.usda.gov/

#### Wikidata (FREE)
- 20,000+ food items
- Aliases in multiple languages
- https://www.wikidata.org/

#### Open Food Facts (FREE)
- 2.8M+ products
- User-contributed
- https://world.openfoodfacts.org/

---

## Score Calculation Examples

### Example 1: Pad Thai

```python
recipe = {
  "name": "Pad Thai",
  "source": "TheMealDB",
  "ingredients": ["rice noodles", "shrimp", "eggs", ...],
  "has_image": True,
  "instructions": ["Step 1...", "Step 2...", ...],
  "tags": ["thai", "noodles", "spicy"]
}

# Component scores:
google_trends = 85  # Very popular search term
platform_engagement = 92  # High ratings on AllRecipes
quality = 95  # Complete recipe with images
recency = 60  # Not currently trending, but steady

# Final score:
final = (85 * 0.4) + (92 * 0.3) + (95 * 0.2) + (60 * 0.1)
      = 34 + 27.6 + 19 + 6
      = 86.6
```

### Example 2: Obscure Regional Dish

```python
recipe = {
  "name": "Faina (Chickpea Flatbread)",
  "source": "MyFridge",
  ...
}

# Component scores:
google_trends = 15  # Low search volume
platform_engagement = 30  # Few ratings
quality = 85  # Good recipe, but niche
recency = 40  # Not trending

# Final score:
final = (15 * 0.4) + (30 * 0.3) + (85 * 0.2) + (40 * 0.1)
      = 6 + 9 + 17 + 4
      = 36
```

---

## Testing the System

### Manual Test (Single Recipe)

```bash
cd backend
source venv/bin/activate
python -c "
from scraper.real_popularity_system import RealPopularityScorer
scorer = RealPopularityScorer()
score = scorer.calculate_real_popularity({'name': 'Pad Thai'})
print(f'Score: {score}')
"
```

### Batch Test (All Recipes)

```bash
cd backend
python scraper/real_popularity_system.py
```

### Compare Old vs New Scores

```bash
cd backend
python scraper/compare_scores.py
```

---

## Monitoring & Updates

### Weekly Update Script

```bash
#!/bin/bash
# weekly_update.sh

cd /path/to/MyFridge/backend
source venv/bin/activate

echo "🔄 Starting weekly popularity update..."
python scraper/real_popularity_system.py --incremental

if [ $? -eq 0 ]; then
  echo "✅ Update successful!"
  git add data/recipes.json
  git commit -m "chore: Weekly popularity scores update"
  git push
else
  echo "❌ Update failed!"
  exit 1
fi
```

### Monitoring Dashboard

Track key metrics:
- Average score changes week-over-week
- Top 10 trending recipes
- Recipes with biggest score changes
- API call counts and costs

---

## Cost Estimation

### Free Tier (Current Plan)

```
Google Trends: FREE (public API)
TheMealDB: FREE (100 calls/day)
Food.com dataset: FREE (one-time download)
Wikidata: FREE

Total cost: $0/month
```

### Paid Tier (Enhanced Data)

```
Spoonacular API: $29/month (5,000 calls)
AllRecipes scraping: $0 (self-hosted)
Google Trends: FREE

Total cost: ~$29/month
```

### Enterprise Tier (Full Coverage)

```
Spoonacular API: $149/month (50,000 calls)
Edamam API: $49/month
RapidAPI Recipe APIs: $50/month
Cloud hosting (cron jobs): $10/month

Total cost: ~$258/month
```

---

## Next Steps

1. **Install pytrends**: `pip install pytrends`
2. **Test Google Trends**: Run `real_popularity_system.py` on 10 recipes
3. **Build alias database**: Expand `food_aliases.json` to 1,000+ items
4. **Set up weekly cron**: Automate score updates
5. **Add platform APIs**: Integrate AllRecipes/Spoonacular
6. **Monitor results**: Track score changes and user engagement

---

## Files

```
backend/
├── scraper/
│   ├── real_popularity_system.py    # Main scoring engine
│   ├── add_popularity_scores.py     # Old heuristic system (deprecated)
│   └── compare_scores.py            # Compare old vs new scores
├── data/
│   ├── recipes.json                 # Main recipe database
│   ├── food_aliases.json            # Food name aliases
│   └── popularity_cache.json        # Cached Google Trends data
└── services/
    └── recipe_service.py            # Recipe serving logic
```

---

## Questions?

- **How often to update?** Weekly for trends, monthly for full refresh
- **What about seasonal recipes?** Recency boost handles this (10%)
- **Expensive to run?** No, Google Trends is free, and we cache results
- **Will it slow down the app?** No, scoring runs offline, not on-demand

---

**Status:** 🚧 Implementation Ready  
**Next:** Install dependencies and test on sample recipes

