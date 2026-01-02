"""SQLAlchemy database models."""
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Enum
from sqlalchemy.sql import func
from datetime import date
import enum

from .database import Base


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


class FridgeItem(Base):
    """Model for items stored in the fridge/freezer/pantry."""
    __tablename__ = "fridge_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    quantity = Column(Float, nullable=False, default=1)
    unit = Column(String(20), default="pieces")  # pieces, grams, liters, etc.
    location = Column(String(20), default=Location.FRIDGE.value)
    category = Column(String(20), default=Category.OTHER.value)
    expiration_date = Column(Date, nullable=True)
    added_date = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(String(255), nullable=True)

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

