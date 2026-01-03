#!/usr/bin/env python3
"""
Real-world popularity scoring system for recipes.

Data sources:
1. Google Trends API - Interest over time (90 days + 5-year baseline)
2. Recipe platform APIs - Ratings, reviews, saves, views
3. Food alias database - Normalize recipe names for better matching

Score components:
- Google Trends (40%): Current buzz + long-term interest
- Platform engagement (30%): Ratings, reviews, saves
- Recipe quality (20%): Completeness, instructions, images
- Recency boost (10%): Recent trending topics

Update frequency: Weekly/monthly automated refresh
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
import time
import warnings

# Suppress pandas FutureWarnings
warnings.filterwarnings('ignore', category=FutureWarning)

# TODO: Install these packages
# pip install pytrends requests-cache

try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False
    print("⚠️  pytrends not installed. Run: pip install pytrends")

try:
    import requests
    from requests_cache import CachedSession
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️  requests not installed. Run: pip install requests requests-cache")


class FoodAliasDatabase:
    """Manages food name aliases for better matching."""
    
    def __init__(self):
        self.aliases = {}
        self.load_aliases()
    
    def load_aliases(self):
        """Load or create food alias database."""
        # TODO: Build comprehensive alias database
        # For now, start with common aliases
        self.aliases = {
            "pad thai": ["thai noodles", "phad thai", "phat thai"],
            "scrambled eggs": ["scrambled egg", "eggs scrambled"],
            "fried rice": ["chinese fried rice", "egg fried rice"],
            "pizza": ["pizza margherita", "cheese pizza"],
            "pasta": ["spaghetti", "fettuccine", "penne"],
            "tacos": ["taco", "mexican tacos"],
            "curry": ["indian curry", "thai curry", "chicken curry"],
            "burger": ["hamburger", "cheeseburger"],
            "salad": ["green salad", "mixed salad"],
            "soup": ["vegetable soup", "chicken soup"],
        }
    
    def get_search_terms(self, recipe_name):
        """Get all search terms for a recipe (name + aliases)."""
        name_lower = recipe_name.lower().strip()
        
        # Check if this name has aliases
        for main_term, aliases in self.aliases.items():
            if main_term in name_lower or name_lower in aliases:
                return [main_term] + aliases
        
        # No aliases, use the recipe name
        return [name_lower]


class GoogleTrendsCollector:
    """Collects Google Trends data for recipes."""
    
    def __init__(self):
        if PYTRENDS_AVAILABLE:
            self.pytrends = TrendReq(hl='en-US', tz=360)
        else:
            self.pytrends = None
    
    def get_interest_score(self, recipe_name, alias_db):
        """Get Google Trends interest score (0-100)."""
        if not self.pytrends:
            return 50  # Default if API not available
        
        try:
            search_terms = alias_db.get_search_terms(recipe_name)
            primary_term = search_terms[0]
            
            # Get 90-day trend
            timeframe_90d = 'today 3-m'
            self.pytrends.build_payload([primary_term], timeframe=timeframe_90d)
            interest_90d = self.pytrends.interest_over_time()
            
            # Get 5-year baseline
            timeframe_5y = 'today 5-y'
            self.pytrends.build_payload([primary_term], timeframe=timeframe_5y)
            interest_5y = self.pytrends.interest_over_time()
            
            # Calculate scores
            recent_avg = interest_90d[primary_term].mean() if not interest_90d.empty else 0
            baseline_avg = interest_5y[primary_term].mean() if not interest_5y.empty else 0
            
            # Weighted score: 60% recent, 40% baseline
            score = (recent_avg * 0.6) + (baseline_avg * 0.4)
            
            # Rate limiting
            time.sleep(1)  # Google Trends rate limits
            
            return min(100, max(0, score))
            
        except Exception as e:
            print(f"❌ Google Trends error for '{recipe_name}': {e}")
            return 50  # Default on error
    
    def batch_get_trends(self, recipe_names, alias_db):
        """Batch fetch trends for multiple recipes."""
        results = {}
        
        for i, recipe_name in enumerate(recipe_names):
            print(f"📊 Fetching trends: {i+1}/{len(recipe_names)} - {recipe_name}")
            results[recipe_name] = self.get_interest_score(recipe_name, alias_db)
        
        return results


class PlatformEngagementCollector:
    """Collects engagement data from recipe platforms."""
    
    def __init__(self):
        # Use cached session to avoid hammering APIs
        if REQUESTS_AVAILABLE:
            self.session = CachedSession('recipe_cache', expire_after=86400)  # 24h cache
        else:
            self.session = None
    
    def get_allrecipes_engagement(self, recipe_name):
        """Get AllRecipes ratings and review count."""
        # TODO: Implement AllRecipes API/scraping
        # For now, return dummy data
        return {
            'rating': 4.5,
            'review_count': 1200,
            'save_count': 800
        }
    
    def get_foodcom_engagement(self, recipe_name):
        """Get Food.com engagement metrics."""
        # TODO: Implement Food.com API
        return {
            'rating': 4.2,
            'review_count': 500,
            'save_count': 300
        }
    
    def get_engagement_score(self, recipe_name):
        """Aggregate engagement score from all platforms (0-100)."""
        # TODO: Implement real API calls
        # For now, return a synthetic score
        
        # Example calculation:
        # score = (avg_rating / 5.0 * 50) + (log(review_count) * 10) + (log(save_count) * 5)
        
        return 60  # Placeholder


class RealPopularityScorer:
    """Main popularity scoring engine."""
    
    def __init__(self):
        self.alias_db = FoodAliasDatabase()
        self.trends_collector = GoogleTrendsCollector()
        self.engagement_collector = PlatformEngagementCollector()
    
    def calculate_quality_score(self, recipe):
        """Calculate recipe quality score (0-100)."""
        score = 0
        
        # Has description
        if recipe.get('description') and len(recipe.get('description', '')) > 20:
            score += 15
        
        # Has tags
        if recipe.get('tags') and len(recipe.get('tags', [])) > 0:
            score += 15
        
        # Has image
        if recipe.get('image') or recipe.get('image_url'):
            score += 20
        
        # Has detailed instructions
        instructions = recipe.get('instructions', [])
        if instructions and len(instructions) >= 3:
            score += 25
        
        # Has timing info
        if recipe.get('total_time') or (recipe.get('prep_time') and recipe.get('cook_time')):
            score += 15
        
        # Has reasonable number of ingredients
        ingredients = recipe.get('ingredients', [])
        if 3 <= len(ingredients) <= 15:
            score += 10
        
        return min(100, score)
    
    def calculate_recency_boost(self, recipe):
        """Calculate recency boost (0-100) for trending topics."""
        # TODO: Check if recipe matches current trending topics
        # For now, return neutral
        return 50
    
    def calculate_real_popularity(self, recipe):
        """Calculate real-world popularity score (0-100)."""
        recipe_name = recipe.get('name', 'Unknown')
        
        # Component scores (0-100 each)
        google_trends = self.trends_collector.get_interest_score(recipe_name, self.alias_db)
        platform_engagement = self.engagement_collector.get_engagement_score(recipe_name)
        quality = self.calculate_quality_score(recipe)
        recency = self.calculate_recency_boost(recipe)
        
        # Weighted final score
        final_score = (
            google_trends * 0.40 +
            platform_engagement * 0.30 +
            quality * 0.20 +
            recency * 0.10
        )
        
        return round(final_score, 1)
    
    def score_all_recipes(self, recipes_file):
        """Score all recipes and update the database."""
        # Load recipes
        with open(recipes_file, 'r', encoding='utf-8') as f:
            recipes = json.load(f)
        
        print(f"📖 Loaded {len(recipes)} recipes")
        print("🔄 Starting real popularity scoring...")
        print("⚠️  Note: Google Trends API has rate limits. This may take a while.\n")
        
        # Score each recipe
        for i, recipe in enumerate(recipes):
            recipe_name = recipe.get('name', 'Unknown')
            print(f"[{i+1}/{len(recipes)}] Scoring: {recipe_name}", flush=True)
            
            # Calculate real popularity
            real_score = self.calculate_real_popularity(recipe)
            print(f"    → Score: {real_score:.1f}", flush=True)
            
            # Store both scores for comparison
            recipe['popularity_score_old'] = recipe.get('popularity_score', 0)
            recipe['popularity_score'] = real_score
            recipe['popularity_last_updated'] = datetime.now().isoformat()
        
        # Sort by new popularity
        recipes.sort(key=lambda r: r.get('popularity_score', 0), reverse=True)
        
        # Save
        with open(recipes_file, 'w', encoding='utf-8') as f:
            json.dump(recipes, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Done! Updated {len(recipes)} recipes with real popularity scores")
        
        # Show comparison
        print("\n📊 Top 10 by Real Popularity:")
        for i, recipe in enumerate(recipes[:10], 1):
            name = recipe.get('name')
            old = recipe.get('popularity_score_old', 0)
            new = recipe.get('popularity_score', 0)
            diff = new - old
            print(f"  {i}. {name}")
            print(f"     Old: {old:.1f} → New: {new:.1f} (Δ {diff:+.1f})")


def main():
    """Main entry point."""
    print("=" * 70)
    print("🔥 REAL-WORLD POPULARITY SCORING SYSTEM")
    print("=" * 70)
    print()
    
    if not PYTRENDS_AVAILABLE:
        print("❌ Missing dependency: pytrends")
        print("📦 Install: pip install pytrends")
        print()
    
    if not REQUESTS_AVAILABLE:
        print("❌ Missing dependency: requests")
        print("📦 Install: pip install requests requests-cache")
        print()
    
    # Get recipes file
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / 'data'
    recipes_file = data_dir / 'recipes.json'
    
    if not recipes_file.exists():
        print(f"❌ Error: {recipes_file} not found!")
        return
    
    # Ask user to confirm
    print("⚠️  WARNING: This will make many API calls to Google Trends.")
    print("   Google has rate limits. This may take 30-60 minutes for 225 recipes.")
    print()
    response = input("Continue? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("❌ Cancelled")
        return
    
    # Run scoring
    scorer = RealPopularityScorer()
    scorer.score_all_recipes(recipes_file)


if __name__ == '__main__':
    main()

