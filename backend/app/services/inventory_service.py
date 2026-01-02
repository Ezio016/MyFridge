"""Inventory service for CRUD operations on fridge items."""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import date, timedelta
from typing import Optional

from ..models import FridgeItem
from ..schemas import FridgeItemCreate, FridgeItemUpdate


def get_all_items(db: Session, skip: int = 0, limit: int = 100) -> list[FridgeItem]:
    """Get all fridge items."""
    return db.query(FridgeItem).offset(skip).limit(limit).all()


def get_item_by_id(db: Session, item_id: int) -> Optional[FridgeItem]:
    """Get a single fridge item by ID."""
    return db.query(FridgeItem).filter(FridgeItem.id == item_id).first()


def create_item(db: Session, item: FridgeItemCreate) -> FridgeItem:
    """Create a new fridge item."""
    db_item = FridgeItem(
        name=item.name,
        quantity=item.quantity,
        unit=item.unit,
        location=item.location.value,
        category=item.category.value,
        expiration_date=item.expiration_date,
        notes=item.notes,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_item(db: Session, item_id: int, item_update: FridgeItemUpdate) -> Optional[FridgeItem]:
    """Update an existing fridge item."""
    db_item = get_item_by_id(db, item_id)
    if not db_item:
        return None
    
    update_data = item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(value, 'value'):  # Handle enums
            value = value.value
        setattr(db_item, field, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_item(db: Session, item_id: int) -> bool:
    """Delete a fridge item."""
    db_item = get_item_by_id(db, item_id)
    if not db_item:
        return False
    
    db.delete(db_item)
    db.commit()
    return True


def get_expiring_soon(db: Session, days: int = 3) -> list[FridgeItem]:
    """Get items expiring within the specified number of days."""
    threshold = date.today() + timedelta(days=days)
    return db.query(FridgeItem).filter(
        FridgeItem.expiration_date != None,
        FridgeItem.expiration_date <= threshold,
        FridgeItem.expiration_date >= date.today()
    ).all()


def get_expired(db: Session) -> list[FridgeItem]:
    """Get all expired items."""
    return db.query(FridgeItem).filter(
        FridgeItem.expiration_date != None,
        FridgeItem.expiration_date < date.today()
    ).all()


def search_items(db: Session, query: str) -> list[FridgeItem]:
    """Search items by name."""
    return db.query(FridgeItem).filter(
        FridgeItem.name.ilike(f"%{query}%")
    ).all()


def get_inventory_summary(db: Session) -> dict:
    """Get a summary of the inventory for AI context."""
    items = get_all_items(db)
    
    summary = {
        "total_items": len(items),
        "items": [],
        "expiring_soon": [],
        "by_location": {"fridge": [], "freezer": [], "pantry": []},
    }
    
    for item in items:
        item_info = {
            "name": item.name,
            "quantity": f"{item.quantity} {item.unit}",
            "location": item.location,
            "category": item.category,
            "expiry_status": item.expiry_status,
            "days_until_expiry": item.days_until_expiry,
        }
        summary["items"].append(item_info)
        
        if item.expiry_status == "expiring_soon":
            summary["expiring_soon"].append(item_info)
        
        if item.location in summary["by_location"]:
            summary["by_location"][item.location].append(item_info)
    
    return summary

