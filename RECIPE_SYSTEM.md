# MyFridge Recipe System 🍳

## Overview

MyFridge uses a **hybrid approach** combining a curated recipe database with AI assistance:

1. **Recipe Database** - Real, tested recipes from various sources
2. **AI Companion** - Smart assistant that helps you cook, modify recipes, and make suggestions

## Why This Approach?

✅ **Real Recipes** - No AI hallucinations, all recipes are tested and real
✅ **Fast Browsing** - Instant loading from local database (no API calls)
✅ **Structured Data** - Consistent format, searchable, filterable
✅ **AI Enhancement** - AI helps modify recipes, suggest substitutions, guide cooking
✅ **Cost Effective** - Only use AI when needed (chat, modifications, suggestions)

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Quick Mode  │  │ Explore Mode │  │  AI Chat     │  │
│  │  (Database)  │  │  (Database)  │  │ (Companion)  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  BACKEND API (FastAPI)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Recipe     │  │   AI Chef    │  │  Inventory   │  │
│  │   Service    │  │  Companion   │  │   Service    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    DATA SOURCES                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ recipes.json │  │  PostgreSQL  │  │  Groq API    │  │
│  │  (Curated)   │  │  (Inventory) │  │  (AI Chat)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Recipe Database Schema

Each recipe in `backend/data/recipes.json` has:

```json
{
  "id": "unique_recipe_id",
  "source": "BBC Food",
  "name": "Perfect Scrambled Eggs",
  "description": "Creamy, fluffy scrambled eggs in under 5 minutes",
  "prep_time": 2,
  "cook_time": 3,
  "total_time": 5,
  "servings": 2,
  "difficulty": "easy",
  "ingredients": ["4 large eggs", "2 tablespoons milk", ...],
  "instructions": ["Step 1...", "Step 2...", ...],
  "tags": ["breakfast", "quick", "vegetarian", "protein"],
  "cuisine": "American",
  "category": "breakfast",
  "image_url": "https://..."
}
```

## Recipe Sources

Current sources (expandable):
- **MyFridge Curated** - Hand-crafted starter recipes
- **BBC Food** - British recipes (scraper ready)
- **Epicurious** - Professional recipes (planned)
- **Food.com** - Community recipes (planned)
- **The Foreign Fork** - International cuisine (planned)

## API Endpoints

### Recipe Endpoints

```
GET  /api/recipes/              # Get all recipes
GET  /api/recipes/{id}          # Get specific recipe
GET  /api/recipes/random?count=5  # Random recipes for exploration
GET  /api/recipes/quick?max_time=15  # Quick recipes (under X min)
POST /api/recipes/search        # Search with filters
POST /api/recipes/by-ingredients  # Find by ingredients
GET  /api/recipes/tags/{tag}    # Filter by tag
```

### AI Chef Endpoints (Enhanced)

```
POST /api/chat/                 # Chat with AI companion
GET  /api/chat/meal-plan        # AI-suggested meal plan
GET  /api/chat/quick-recipe     # AI-suggested quick recipe
```

## How It Works

### 1. Quick Mode (Lightning ⚡)
- User clicks "Quick" button
- Frontend calls `GET /api/recipes/quick?max_time=15`
- Backend returns recipes from database (under 15 min)
- **No AI involved** - instant results

### 2. Explore Mode (Compass 🧭)
- User clicks "Explore" button
- Frontend calls `GET /api/recipes/random?count=10`
- Backend returns random recipes from database
- **No AI involved** - instant results

### 3. AI Companion (Chat 💬)
- User asks questions or requests modifications
- Frontend calls `POST /api/chat/`
- Backend uses AI to:
  - Suggest recipes from database based on fridge contents
  - Help modify recipes (substitutions, dietary needs)
  - Answer cooking questions
  - Guide through cooking steps

## Adding More Recipes

### Option 1: Run the Scraper

```bash
cd backend
source venv/bin/activate
python scraper/recipe_scraper.py
```

### Option 2: Manual Addition

Edit `backend/data/recipes.json` and add recipes following the schema above.

### Option 3: Scrape Specific Sites

Modify `scraper/recipe_scraper.py` to add new scrapers for:
- Epicurious
- Food.com
- AllRecipes
- Serious Eats
- etc.

## Future Enhancements

### Planned Features
- [ ] User-submitted recipes
- [ ] Recipe ratings and reviews
- [ ] Nutritional information
- [ ] Meal planning calendar
- [ ] Shopping list generation from recipes
- [ ] Recipe collections (favorites, tried, want-to-try)
- [ ] Advanced search (calories, macros, allergens)
- [ ] Recipe scaling (adjust servings)
- [ ] Print-friendly recipe cards

### Scraping Expansion
- [ ] Scrape 100+ recipes from each source
- [ ] Automated weekly scraping
- [ ] Recipe deduplication
- [ ] Image optimization
- [ ] Video tutorials integration

## Development

### Testing Recipe API Locally

```bash
# Start backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Test endpoints
curl http://localhost:8000/api/recipes/
curl http://localhost:8000/api/recipes/quick?max_time=10
curl http://localhost:8000/api/recipes/random?count=3
```

### Adding New Recipe Tags

Common tags to use:
- **Meal Type**: breakfast, lunch, dinner, snack, dessert
- **Speed**: quick, slow-cooker, one-pot, no-cook
- **Diet**: vegetarian, vegan, gluten-free, dairy-free, keto, paleo
- **Protein**: chicken, beef, pork, seafood, tofu, eggs
- **Cuisine**: italian, asian, mexican, mediterranean, american
- **Skill**: easy, medium, hard, beginner-friendly
- **Special**: budget-friendly, kid-friendly, meal-prep, leftover-friendly

## Credits

- Recipe scraping powered by BeautifulSoup4
- AI assistance by Groq (Llama 3.1)
- Recipe sources: BBC Food, Epicurious, Food.com, The Foreign Fork
- Built with FastAPI + React + PostgreSQL

---

**Last Updated**: January 2026
**Version**: 1.0.0

