"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
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


# --- Recipe Schema ---

class Recipe(BaseModel):
    """Schema for a recipe."""
    name: str
    meal_type: str  # breakfast, lunch, dinner, snack
    ingredients: list[str]
    instructions: list[str]
    prep_time_minutes: int
    uses_expiring: bool = False  # True if uses soon-to-expire items

