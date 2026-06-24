# Recipe Customization Feature

## Overview
The AI chat has been repositioned to focus on two specific functions:
1. **"Help finding your favorite recipe"** - For filtering, narrowing down, and sorting recipes (browsing mode)
2. **"Customize this recipe?"** - For modifying recipes with ingredient substitutions and variations (cooking mode)

## Changes Made

### Frontend Changes

#### 1. ChefAssistantChat Component (`components/ChefAssistantChat.jsx`)
- **Updated title**: Changed from "Recipe Assistant" to "Help finding your favorite recipe" for browsing mode
- **Updated title**: Changed from "Modify Recipe" to "Customize Recipe" for cooking mode
- **Updated placeholder**: Changed to "Narrow down, filter, or sort recipes..." for browsing mode
- **Updated placeholder**: Changed to "Ask to customize recipe..." for cooking mode
- **Added customization callback**: When in cooking mode, the chat now triggers `onCustomizeRecipe` callback to initiate the customization flow

#### 2. RecipeModal Component (`components/RecipeModal.jsx`)
- **Added "Customize Recipe" button**: New prominent button appears when viewing full recipe details
- **Added customization prompt**: Helpful prompt showing example customizations (e.g., "Make it vegetarian", "Use chicken instead")
- **Integrated ChefAssistantChat**: AI chat now appears in cooking mode to handle customization requests
- **Added CSS styles**: New styles for customize button and prompt with gradient background

#### 3. ModifiedRecipePage Component (`components/ModifiedRecipePage.jsx`) - NEW
- **Full-page view**: Displays modified recipes in a dedicated full-page view
- **Strikethrough technique**: Shows original ingredients/steps with strikethrough and new ones highlighted
  - Removed items: ~~strikethrough~~
  - Replaced items: ~~old item~~ → **new item**
  - Added items: + **new item**
- **Modified title**: Displays title like "Modified Pad Thai with Chicken" based on the modification
- **AI Chef's Notes**: Shows explanation of the modifications
- **Interactive steps**: Tap to check off steps as you complete them
- **Full recipe card functionality**: Works like a complete recipe card with all features

#### 4. Chef Page (`pages/Chef.jsx`)
- **Added CUSTOMIZING mode**: New mode for displaying modified recipes
- **Added customization state**: Tracks customization data and modification requests
- **Added handleCustomizeRecipe function**: Handles the customization API call
- **Integrated ModifiedRecipePage**: Shows modified recipe view when in customizing mode
- **Updated navigation**: Back button returns to cooking view from modified recipe

### Backend Changes

#### 1. Chat Routes (`backend/app/routes/chat.py`)
- **Added `/customize-recipe` endpoint**: New POST endpoint for recipe customization
- **Imports updated**: Added `modify_recipe` function and new schemas

#### 2. Schemas (`backend/app/schemas.py`)
- **RecipeCustomizationRequest**: New schema for customization requests
  - `recipe`: The original recipe to customize
  - `modification_request`: What to change in the recipe
- **RecipeCustomizationResponse**: New schema for customization responses
  - `ai_response`: AI explanation of modifications
  - `modified_title`: Modified recipe title
  - `ingredients`: Modified ingredients list
  - `steps`: Modified instruction steps
  - `changes`: Dictionary tracking what changed (ingredients/steps)
  - `time`: Modified cooking time
  - `difficulty`: Modified difficulty level

#### 3. AI Chef Service (`backend/app/services/ai_chef.py`)
- **Enhanced `modify_recipe` function**: 
  - Now returns structured JSON with tracked changes
  - Identifies replaced, added, and removed ingredients
  - Tracks modified and added steps
  - Generates appropriate modified recipe title
  - Provides AI explanation of modifications
  - Handles JSON parsing with fallbacks

#### 4. API Client (`frontend/src/api/client.js`)
- **Added `customizeRecipe` method**: New API method for recipe customization

## User Flow

### Browsing Mode (Finding Recipes)
1. User browses recipes on Chef page
2. Opens AI chat (FAB button) showing "Help finding your favorite recipe"
3. Asks for filtering/sorting (e.g., "Show me quick meals under 20 minutes")
4. AI helps narrow down results

### Cooking Mode (Recipe Customization)
1. User selects a recipe to view full details
2. Sees "Customize this recipe?" button with sparkle icon
3. Clicks button to see customization prompt
4. Opens AI chat and asks for modifications (e.g., "Make it vegetarian", "Use chicken instead of shrimp")
5. AI processes the request
6. User is taken to ModifiedRecipePage showing:
   - Modified title (e.g., "Modified Pad Thai with Chicken")
   - AI Chef's notes explaining the changes
   - Ingredients list with strikethrough for changes
   - Steps with modifications highlighted
7. User can cook from the modified recipe or go back

## Visual Design

### Strikethrough Technique
- **Original items being replaced**: Light gray with line-through
- **New/replacement items**: Green color (`#4ade80`) with bold weight
- **Arrow indicator**: Yellow arrow (`→`) between old and new
- **Added items**: Green with `+` prefix

### Color Scheme
- **Customize button**: Purple gradient (`#6366f1` to `#8b5cf6`)
- **AI Response box**: Blue gradient background with left border
- **Modified recipe**: Dark theme with accent colors for changes
- **Done state**: Green success theme

## Example Scenarios

### Scenario 1: Protein Substitution
**Request**: "Use chicken instead of shrimp"
**Result**: 
- Title: "Modified Pad Thai with Chicken"
- Ingredients: ~~500g shrimp~~ → **500g chicken breast**
- Steps updated to reflect chicken cooking time

### Scenario 2: Dietary Restriction
**Request**: "Make it vegetarian"
**Result**:
- Title: "Modified Vegetarian Pad Thai"
- All meat/seafood ingredients replaced with tofu/vegetables
- Steps adjusted for vegetarian cooking methods

### Scenario 3: Ingredient Unavailability
**Request**: "I don't have bell peppers"
**Result**:
- Title: "Modified Stir Fry without Bell Peppers"
- ~~2 bell peppers~~ removed or replaced with available alternatives
- Steps adjusted accordingly

## Technical Notes

- All modifications are tracked with change types: `replaced`, `added`, `removed`, `modified`
- The AI uses Groq's Llama 3.1 model for fast, free customization
- Modified recipes maintain full recipe card functionality (favoriting, step checking, etc.)
- The system gracefully handles API errors with fallback responses
- JSON parsing includes cleanup for markdown code blocks from AI responses

## Future Enhancements

Possible improvements:
- Save customized recipes to user's collection
- Share modified recipes
- Version history of customizations
- Batch customizations (multiple changes at once)
- Voice input for customization requests
- Image generation for modified recipes

