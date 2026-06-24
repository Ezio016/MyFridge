# Dynamic Recipe Filtering with AI Chat

## Overview
The AI chat in browsing mode now **actively filters, sorts, and organizes recipes** based on natural language queries. It's like a smart keyword filter that understands context and intent.

## How It Works

### 1. Open the AI Chat
- Click the floating chat button (💬) on the Chef page
- You'll see: **"Help finding your favorite recipe"**

### 2. Type What You're Looking For
The AI understands natural language and automatically applies filters/sorts:

#### Example Queries:

**Time-based filtering:**
- "Show me quick meals under 20 minutes"
- "Recipes that take less than 15 minutes"
- "What can I make in under 30 minutes?"

**Readiness filtering:**
- "Show only recipes I can make right now" → Filters to ready-to-cook recipes
- "What can I cook with what I have?" → Shows recipes with all ingredients

**Diet/Cuisine filtering:**
- "Show me vegetarian recipes"
- "Make it vegan"
- "Gluten-free options"
- "Italian dishes"

**Sorting:**
- "Sort by fastest" → Orders by cooking time
- "Show most popular first" → Sorts by popularity
- "Alphabetical order" → A-Z sorting

**Combined queries:**
- "Quick Italian dishes under 20 minutes"
- "Vegetarian recipes I can cook right now"
- "Easiest recipes that use expiring items"
- "Popular dinner recipes under 30 minutes"

**Reset:**
- "Reset all filters"
- "Clear filters"
- "Start over"

### 3. See Results Instantly
- The recipe list updates **automatically**
- The AI confirms what it did (e.g., "✅ Showing only ready-to-cook recipes")
- Scroll through the filtered results

### 4. Refine Further
- Keep chatting to narrow down more
- Example flow:
  1. "Show vegetarian recipes" → 50 results
  2. "Under 20 minutes" → 15 results
  3. "Sort by fastest" → Sorted!

## Quick Action Buttons

Click these for instant filtering:
- **⚡ Quick (under 20m)** → Recipes under 20 minutes
- **✨ Ready to cook** → Only recipes with all ingredients
- **🥬 Vegetarian** → Vegetarian recipes only
- **🔥 Most popular** → Sort by popularity
- **⏱️ Fastest first** → Sort by cooking time
- **🔄 Reset filters** → Clear all filters

## Technical Details

### What Happens Behind the Scenes:
1. Your message is sent to `/chat/controls` endpoint
2. AI parses your intent using Groq's Llama model
3. Returns structured filter/sort actions
4. Frontend applies these to `controlsState`
5. Recipe list re-renders with filtered results

### Supported Filters:
- `maxTimeMinutes` - Maximum cooking time
- `readyOnly` - Only show ready-to-cook recipes
- `expiringOnly` - Use expiring ingredients
- `difficulty` - Easy, medium, hard
- `diet` - Vegetarian, vegan, gluten-free
- `excludeIngredients` - Exclude specific items
- `mealType` - Breakfast, lunch, dinner, snack

### Supported Sorts:
- `ranked` - Best match (default)
- `time_asc` / `fastest` - Fastest first
- `popularity` / `most_popular` - Most popular
- `fewest_missing` - Least missing ingredients
- `alphabetical` - A-Z

## Advanced Examples

### Complex Multi-Filter:
**Query**: "Show me easy vegetarian dinner recipes under 30 minutes that I can cook right now, sorted by most popular"

**AI Applies:**
```javascript
{
  filters: {
    difficulty: ['easy'],
    maxTimeMinutes: 30,
    readyOnly: true,
    mealType: 'dinner'
  },
  customization: {
    diet: 'vegetarian'
  },
  sort: {
    by: 'most_popular',
    direction: 'desc'
  }
}
```

### Exclusion Filter:
**Query**: "No onions, no garlic"

**AI Applies:**
```javascript
{
  customization: {
    excludeIngredients: ['onions', 'garlic']
  }
}
```

### Progressive Refinement:
```
User: "Show dinner recipes"
AI: ✅ Filtering to dinner recipes

User: "Only vegetarian"
AI: ✅ Applied vegetarian filter

User: "Under 25 minutes"
AI: ✅ Filtering to recipes under 25 minutes

User: "Sort by fastest"
AI: ✅ Sorting by fastest first
```

## Benefits Over Manual Filters

### Traditional UI Filters:
- Click dropdown → Select option → Apply
- Multiple clicks for multiple filters
- Need to know exact filter names
- Limited combinations

### AI Chat Filtering:
- Type one sentence → Done ✅
- Natural language (say it how you think it)
- Understands context and synonyms
- Combines multiple filters automatically
- Conversational refinement

## Tips for Best Results

1. **Be specific**: "Quick vegetarian meals" better than just "food"
2. **Use numbers**: "Under 20 minutes" better than "fast"
3. **Combine criteria**: "Easy Italian recipes I can make now"
4. **Refine progressively**: Start broad, then narrow down
5. **Use quick actions**: Instant common filters

## Fallback Behavior

If the AI doesn't understand or API fails:
- Falls back to keyword matching
- Shows helpful error message
- Suggests trying simpler queries
- Manual filters still available in UI

## Performance

- **Response time**: 1-2 seconds (AI processing)
- **No page refresh**: Updates instantly
- **Works offline**: Falls back to client-side filtering
- **Free tier**: Uses Groq's free API

## Future Enhancements

Possible improvements:
- Voice input for queries
- Saved search presets
- Multi-language support
- Learning user preferences
- Suggested follow-up refinements
- Visual feedback of applied filters

