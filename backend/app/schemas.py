"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field, EmailStr
from datetime import date, datetime
from typing import Optional, Any
from enum import Enum


class Location(str, Enum):
    FRIDGE = "fridge"
    FREEZER = "freezer"
    PANTRY = "pantry"


class Category(str, Enum):
    DAIRY = "dairy"
    MEAT = "meat"
    SEAFOOD = "seafood"
    VEGETABLE = "vegetable"
    FRUIT = "fruit"
    GRAIN = "grain"
    BEVERAGE = "beverage"
    CONDIMENT = "condiment"
    SNACK = "snack"
    LEFTOVER = "leftover"
    OTHER = "other"


# ============================================================
# AUTH SCHEMAS
# ============================================================

class UserRegister(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    name: Optional[str] = Field(default=None, max_length=100)


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class TokenData(BaseModel):
    """Schema for decoded JWT token data."""
    user_id: Optional[int] = None
    email: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user response (no password)."""
    id: int
    email: str
    name: Optional[str] = None
    created_at: datetime
    is_active: bool = True

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    name: Optional[str] = Field(default=None, max_length=100)
    email: Optional[EmailStr] = None


# ============================================================
# FLAVOR PROFILE SCHEMAS
# ============================================================

class FlavorVector(BaseModel):
    """8D flavor vector."""
    sweet: float = Field(default=0.0, ge=0.0, le=1.0)
    salty: float = Field(default=0.0, ge=0.0, le=1.0)
    sour: float = Field(default=0.0, ge=0.0, le=1.0)
    bitter: float = Field(default=0.0, ge=0.0, le=1.0)
    umami: float = Field(default=0.0, ge=0.0, le=1.0)
    spicy: float = Field(default=0.0, ge=0.0, le=1.0)
    fatty: float = Field(default=0.0, ge=0.0, le=1.0)
    aromatic: float = Field(default=0.0, ge=0.0, le=1.0)

    def to_list(self) -> list[float]:
        return [self.sweet, self.salty, self.sour, self.bitter,
                self.umami, self.spicy, self.fatty, self.aromatic]


class FlavorProfileResponse(BaseModel):
    """Schema for flavor profile response."""
    dimensions: dict[str, float]
    dominant_flavors: list[str] = []
    description: str = "balanced"


class UserFlavorProfileResponse(BaseModel):
    """Schema for user flavor profile response."""
    user_id: int
    profile: FlavorVector
    interaction_count: int = 0
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================
# RECIPE SCHEMAS
# ============================================================

class IngredientBase(BaseModel):
    """Base schema for an ingredient."""
    name: str
    amount: Optional[str] = None
    unit: Optional[str] = None
    role: str = "secondary"
    is_optional: bool = False


class RecipeBase(BaseModel):
    """Base schema for recipe."""
    name: str
    description: Optional[str] = None
    prep_time: Optional[int] = None
    cook_time: Optional[int] = None
    total_time: Optional[int] = None
    servings: int = 4
    difficulty: str = "medium"
    cuisine: Optional[str] = None
    category: Optional[str] = None
    tags: list[str] = []
    image_url: Optional[str] = None


class RecipeCreate(RecipeBase):
    """Schema for creating a recipe."""
    instructions: list[str] = []
    ingredients: list[str] = []  # Raw ingredient strings


class RecipeResponse(RecipeBase):
    """Schema for recipe response."""
    id: str  # external_id
    instructions: list[str] = []
    ingredients: list[str] = []
    mainIngredients: list[str] = []
    optionalIngredients: list[str] = []
    popularity_score: float = 0.0
    source: Optional[str] = None
    flavor_profile: Optional[FlavorProfileResponse] = None
    ingredient_vector: Optional[list[int]] = None

    class Config:
        from_attributes = True


class RecipeWithSimilarity(RecipeResponse):
    """Recipe with similarity score."""
    similarity: float = 0.0


class RecipeSimilarResponse(BaseModel):
    """Response for similar recipes endpoint."""
    recipe_id: str
    similar_recipes: list[RecipeWithSimilarity]


# ============================================================
# RECIPE INTERACTION SCHEMAS
# ============================================================

class InteractionType(str, Enum):
    VIEW = "view"
    LIKE = "like"
    COOK = "cook"
    SHOP = "shop"
    UNLIKE = "unlike"


class RecipeInteractionRequest(BaseModel):
    """Schema for logging a recipe interaction."""
    recipe_id: str
    interaction_type: InteractionType


class RecipeInteractionResponse(BaseModel):
    """Response after logging interaction."""
    success: bool
    interaction_type: str
    updated_flavor_profile: Optional[FlavorVector] = None


# ============================================================
# RECOMMENDATION SCHEMAS
# ============================================================

class RecommendationRequest(BaseModel):
    """Schema for personalized recommendation request."""
    limit: int = Field(default=10, ge=1, le=50)
    exclude_ids: list[str] = []
    cuisine: Optional[str] = None
    max_time: Optional[int] = None
    difficulty: Optional[str] = None


class RecommendationResponse(BaseModel):
    """Response with personalized recommendations."""
    recipes: list[RecipeResponse]
    user_flavor_profile: Optional[FlavorVector] = None
    match_scores: list[float] = []


# --- Fridge Item Schemas ---

class FridgeItemBase(BaseModel):
    """Base schema for fridge items."""
    name: str = Field(..., min_length=1, max_length=100)
    quantity: float = Field(default=1, gt=0)
    unit: str = Field(default="pieces", max_length=20)
    location: Location = Location.FRIDGE
    category: Category = Category.OTHER
    expiration_date: Optional[date] = None
    notes: Optional[str] = Field(default=None, max_length=255)


class FridgeItemCreate(FridgeItemBase):
    """Schema for creating a new fridge item."""
    pass


class FridgeItemUpdate(BaseModel):
    """Schema for updating a fridge item (all fields optional)."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    quantity: Optional[float] = Field(default=None, gt=0)
    unit: Optional[str] = Field(default=None, max_length=20)
    location: Optional[Location] = None
    category: Optional[Category] = None
    expiration_date: Optional[date] = None
    notes: Optional[str] = Field(default=None, max_length=255)


class FridgeItemResponse(FridgeItemBase):
    """Schema for fridge item response."""
    id: int
    added_date: datetime
    days_until_expiry: Optional[int] = None
    expiry_status: str = "unknown"

    class Config:
        from_attributes = True


# --- Chat Schemas ---

class ChatMessage(BaseModel):
    """Schema for chat message."""
    message: str = Field(..., min_length=1, max_length=10000)


class ChatResponse(BaseModel):
    """Schema for chat response."""
    response: str
    recipes: Optional[list[dict]] = None


# --- Chef Controls Chat Schemas (filter/sort/customization) ---

class ChefControlsState(BaseModel):
    """Serializable UI state for AI Chef controls (filters/sort/customization)."""
    filters: dict = Field(default_factory=dict)
    customization: dict = Field(default_factory=dict)
    sort: dict = Field(default_factory=dict)


class ChefControlsRequest(BaseModel):
    """Schema for Chef controls assistant request."""
    message: str = Field(..., min_length=1, max_length=10000)
    state: ChefControlsState = Field(default_factory=ChefControlsState)
    facets: dict = Field(default_factory=dict)


class ChefControlAction(BaseModel):
    """A small, declarative update to apply to UI state."""
    op: str = Field(..., description="Operation type. Currently only 'set' is supported.")
    path: str = Field(..., description="Dot-path into state, e.g. 'filters.expiringOnly'")
    value: Optional[Any] = None


class ChefControlsResponse(BaseModel):
    """Schema for Chef controls assistant response."""
    assistant_message: str
    actions: list[ChefControlAction] = Field(default_factory=list)
    new_state: ChefControlsState


# --- Recipe Schema ---

class Recipe(BaseModel):
    """Schema for a recipe."""
    name: str
    meal_type: str  # breakfast, lunch, dinner, snack
    ingredients: list[str]
    instructions: list[str]
    prep_time_minutes: int
    uses_expiring: bool = False  # True if uses soon-to-expire items


# --- Recipe Customization Schemas ---

class RecipeCustomizationRequest(BaseModel):
    """Schema for recipe customization request."""
    recipe: dict = Field(..., description="The original recipe to customize")
    modification_request: str = Field(..., min_length=1, max_length=1000, description="What to change in the recipe")


class RecipeCustomizationResponse(BaseModel):
    """Schema for recipe customization response."""
    ai_response: str = Field(..., description="AI explanation of the modifications")
    modified_title: Optional[str] = Field(None, description="Modified recipe title")
    ingredients: list[str] = Field(..., description="Modified ingredients list")
    steps: list[str] = Field(..., description="Modified instruction steps")
    changes: dict = Field(default_factory=dict, description="Tracking of what changed")
    time: Optional[int] = Field(None, description="Modified cooking time in minutes")
    difficulty: Optional[str] = Field(None, description="Modified difficulty level")


# Fix forward reference for Token schema
Token.model_rebuild()

