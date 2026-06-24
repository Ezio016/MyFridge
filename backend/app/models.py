"""SQLAlchemy database models."""
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, Text, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import date
import enum

from .database import Base


# ============================================================
# ENUMS
# ============================================================

class Location(str, enum.Enum):
    """Storage location for food items."""
    FRIDGE = "fridge"
    FREEZER = "freezer"
    PANTRY = "pantry"


class Category(str, enum.Enum):
    """Food category."""
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


class IngredientRole(str, enum.Enum):
    """Role of ingredient in a recipe."""
    MAIN = "main"
    SECONDARY = "secondary"
    SEASONING = "seasoning"
    GARNISH = "garnish"


# ============================================================
# USER MODELS
# ============================================================

class User(Base):
    """User account for authentication and personalization."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)

    # Relationships
    flavor_profile = relationship("UserFlavorProfile", back_populates="user", uselist=False)
    favorites = relationship("FavoriteRecipe", back_populates="user")
    fridge_items = relationship("FridgeItem", back_populates="user")
    interactions = relationship("UserRecipeInteraction", back_populates="user")

    # Social graph: users this user follows / is followed by
    following = relationship(
        "UserFollow",
        foreign_keys="UserFollow.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan",
    )
    followers = relationship(
        "UserFollow",
        foreign_keys="UserFollow.followee_id",
        back_populates="followee",
        cascade="all, delete-orphan",
    )


class UserFollow(Base):
    """Directed social-graph edge: ``follower_id`` follows ``followee_id``.

    These edges form the network used by the PageRank influence model:
    a follow edge is treated as an endorsement that flows influence from the
    follower toward the followee (i.e. people you follow accrue authority).
    """
    __tablename__ = "user_follows"
    __table_args__ = (
        UniqueConstraint("follower_id", "followee_id", name="uq_follower_followee"),
    )

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    followee_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    followee = relationship("User", foreign_keys=[followee_id], back_populates="followers")


class UserFlavorProfile(Base):
    """User's taste preferences as an 8D flavor vector."""
    __tablename__ = "user_flavor_profiles"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    sweet = Column(Float, default=0.0)
    salty = Column(Float, default=0.0)
    sour = Column(Float, default=0.0)
    bitter = Column(Float, default=0.0)
    umami = Column(Float, default=0.0)
    spicy = Column(Float, default=0.0)
    fatty = Column(Float, default=0.0)
    aromatic = Column(Float, default=0.0)
    interaction_count = Column(Integer, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="flavor_profile")

    def to_vector(self) -> list[float]:
        """Return flavor profile as a list."""
        return [self.sweet, self.salty, self.sour, self.bitter, 
                self.umami, self.spicy, self.fatty, self.aromatic]


class UserRecipeInteraction(Base):
    """Track user interactions with recipes for recommendation."""
    __tablename__ = "user_recipe_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    interaction_type = Column(String(20), nullable=False)  # view, like, cook, shop
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="interactions")
    recipe = relationship("Recipe", back_populates="interactions")


class FavoriteRecipe(Base):
    """User's saved/favorite recipes."""
    __tablename__ = "favorite_recipes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="favorites")
    recipe = relationship("Recipe", back_populates="favorited_by")


# ============================================================
# RECIPE MODELS
# ============================================================

class Recipe(Base):
    """Recipe with all metadata."""
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(100), unique=True, index=True)  # Original ID from JSON
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    prep_time = Column(Integer, nullable=True)
    cook_time = Column(Integer, nullable=True)
    total_time = Column(Integer, nullable=True)
    servings = Column(Integer, default=4)
    difficulty = Column(String(20), default="medium")
    cuisine = Column(String(50), nullable=True, index=True)
    category = Column(String(50), nullable=True, index=True)
    instructions = Column(JSON, nullable=True)  # List of steps
    tags = Column(JSON, nullable=True)  # List of tags
    image_url = Column(String(500), nullable=True)
    source = Column(String(100), nullable=True)
    popularity_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    vector = relationship("RecipeVector", back_populates="recipe", uselist=False)
    flavor_profile = relationship("RecipeFlavorProfile", back_populates="recipe", uselist=False)
    ingredients = relationship("RecipeIngredient", back_populates="recipe")
    favorited_by = relationship("FavoriteRecipe", back_populates="recipe")
    interactions = relationship("UserRecipeInteraction", back_populates="recipe")

    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "id": self.external_id or str(self.id),
            "name": self.name,
            "description": self.description,
            "prep_time": self.prep_time,
            "cook_time": self.cook_time,
            "total_time": self.total_time,
            "servings": self.servings,
            "difficulty": self.difficulty,
            "cuisine": self.cuisine,
            "category": self.category,
            "instructions": self.instructions or [],
            "tags": self.tags or [],
            "image_url": self.image_url,
            "source": self.source,
            "popularity_score": self.popularity_score,
            "ingredients": [ri.to_string() for ri in self.ingredients] if self.ingredients else [],
            "mainIngredients": [ri.to_string() for ri in self.ingredients if ri.role == "main"] if self.ingredients else [],
            "optionalIngredients": [ri.to_string() for ri in self.ingredients if ri.is_optional] if self.ingredients else [],
        }


class RecipeVector(Base):
    """Pre-computed ingredient and method vectors for a recipe."""
    __tablename__ = "recipe_vectors"

    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True)
    ingredient_vector = Column(JSON, nullable=False)  # 44D binary vector
    method_vector = Column(JSON, nullable=True)  # 12D binary vector for cooking methods
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    recipe = relationship("Recipe", back_populates="vector")

    def to_list(self) -> list[int]:
        """Return ingredient vector as list."""
        return self.ingredient_vector if isinstance(self.ingredient_vector, list) else []


class RecipeFlavorProfile(Base):
    """Pre-computed flavor profile for a recipe."""
    __tablename__ = "recipe_flavor_profiles"

    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True)
    sweet = Column(Float, default=0.0)
    salty = Column(Float, default=0.0)
    sour = Column(Float, default=0.0)
    bitter = Column(Float, default=0.0)
    umami = Column(Float, default=0.0)
    spicy = Column(Float, default=0.0)
    fatty = Column(Float, default=0.0)
    aromatic = Column(Float, default=0.0)
    dominant_flavors = Column(JSON, nullable=True)  # Top 3 flavors
    flavor_description = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    recipe = relationship("Recipe", back_populates="flavor_profile")

    def to_vector(self) -> list[float]:
        """Return as 8D vector."""
        return [self.sweet, self.salty, self.sour, self.bitter,
                self.umami, self.spicy, self.fatty, self.aromatic]

    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "dimensions": {
                "sweet": self.sweet,
                "salty": self.salty,
                "sour": self.sour,
                "bitter": self.bitter,
                "umami": self.umami,
                "spicy": self.spicy,
                "fatty": self.fatty,
                "aromatic": self.aromatic,
            },
            "dominant_flavors": self.dominant_flavors or [],
            "description": self.flavor_description or "balanced",
        }


# ============================================================
# INGREDIENT MODELS
# ============================================================

class Ingredient(Base):
    """Master list of ingredients with their properties."""
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(50), nullable=True)  # protein, vegetable, grain, etc.
    is_common = Column(Boolean, default=False)  # Common pantry staple

    # Relationships
    flavor = relationship("IngredientFlavor", back_populates="ingredient", uselist=False)
    recipe_uses = relationship("RecipeIngredient", back_populates="ingredient")


class IngredientFlavor(Base):
    """Flavor profile for an ingredient (8D vector)."""
    __tablename__ = "ingredient_flavors"

    ingredient_id = Column(Integer, ForeignKey("ingredients.id", ondelete="CASCADE"), primary_key=True)
    sweet = Column(Float, default=0.0)
    salty = Column(Float, default=0.0)
    sour = Column(Float, default=0.0)
    bitter = Column(Float, default=0.0)
    umami = Column(Float, default=0.0)
    spicy = Column(Float, default=0.0)
    fatty = Column(Float, default=0.0)
    aromatic = Column(Float, default=0.0)

    ingredient = relationship("Ingredient", back_populates="flavor")

    def to_vector(self) -> list[float]:
        """Return as 8D vector."""
        return [self.sweet, self.salty, self.sour, self.bitter,
                self.umami, self.spicy, self.fatty, self.aromatic]


class RecipeIngredient(Base):
    """Junction table linking recipes to ingredients with quantities."""
    __tablename__ = "recipe_ingredients"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id", ondelete="SET NULL"), nullable=True)
    ingredient_name = Column(String(100), nullable=False)  # Original text
    amount = Column(String(50), nullable=True)  # "1 cup", "2 lbs"
    unit = Column(String(30), nullable=True)
    original_text = Column(String(255), nullable=True)  # Full original string
    role = Column(String(20), default="secondary")  # main, secondary, seasoning, garnish
    is_optional = Column(Boolean, default=False)
    classification = Column(String(20), nullable=True)  # essential, common, specialty

    recipe = relationship("Recipe", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="recipe_uses")

    def to_string(self) -> str:
        """Return ingredient as formatted string."""
        if self.original_text:
            return self.original_text
        if self.amount:
            return f"{self.amount} {self.ingredient_name}"
        return self.ingredient_name


# ============================================================
# FRIDGE ITEM (Updated with user relationship)
# ============================================================

class FridgeItem(Base):
    """Model for items stored in the fridge/freezer/pantry."""
    __tablename__ = "fridge_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(100), nullable=False, index=True)
    quantity = Column(Float, nullable=False, default=1)
    unit = Column(String(20), default="pieces")
    location = Column(String(20), default=Location.FRIDGE.value)
    category = Column(String(20), default=Category.OTHER.value)
    expiration_date = Column(Date, nullable=True)
    added_date = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(String(255), nullable=True)

    user = relationship("User", back_populates="fridge_items")

    @property
    def days_until_expiry(self) -> int | None:
        """Calculate days until expiration."""
        if self.expiration_date is None:
            return None
        return (self.expiration_date - date.today()).days

    @property
    def expiry_status(self) -> str:
        """Get expiry status: fresh, expiring_soon, expired."""
        days = self.days_until_expiry
        if days is None:
            return "unknown"
        if days < 0:
            return "expired"
        if days <= 3:
            return "expiring_soon"
        return "fresh"

