"""Inventory API routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..schemas import (
    FridgeItemCreate, 
    FridgeItemUpdate, 
    FridgeItemResponse
)
from ..services import inventory_service

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/", response_model=list[FridgeItemResponse])
def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all items in the fridge."""
    items = inventory_service.get_all_items(db, skip=skip, limit=limit)
    return [_item_to_response(item) for item in items]


@router.get("/expiring", response_model=list[FridgeItemResponse])
def list_expiring_items(
    days: int = Query(3, ge=1, le=14),
    db: Session = Depends(get_db)
):
    """Get items expiring within specified days."""
    items = inventory_service.get_expiring_soon(db, days=days)
    return [_item_to_response(item) for item in items]


@router.get("/expired", response_model=list[FridgeItemResponse])
def list_expired_items(db: Session = Depends(get_db)):
    """Get all expired items."""
    items = inventory_service.get_expired(db)
    return [_item_to_response(item) for item in items]


@router.get("/search", response_model=list[FridgeItemResponse])
def search_items(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    """Search items by name."""
    items = inventory_service.search_items(db, q)
    return [_item_to_response(item) for item in items]


@router.get("/summary")
def get_inventory_summary(db: Session = Depends(get_db)):
    """Get inventory summary for AI context."""
    return inventory_service.get_inventory_summary(db)


@router.get("/{item_id}", response_model=FridgeItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get a single item by ID."""
    item = inventory_service.get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return _item_to_response(item)


@router.post("/", response_model=FridgeItemResponse, status_code=201)
def create_item(item: FridgeItemCreate, db: Session = Depends(get_db)):
    """Add a new item to the fridge."""
    db_item = inventory_service.create_item(db, item)
    return _item_to_response(db_item)


@router.put("/{item_id}", response_model=FridgeItemResponse)
def update_item(
    item_id: int, 
    item: FridgeItemUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing item."""
    db_item = inventory_service.update_item(db, item_id, item)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return _item_to_response(db_item)


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete an item from the fridge."""
    success = inventory_service.delete_item(db, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return None


def _item_to_response(item) -> FridgeItemResponse:
    """Convert database item to response schema."""
    return FridgeItemResponse(
        id=item.id,
        name=item.name,
        quantity=item.quantity,
        unit=item.unit,
        location=item.location,
        category=item.category,
        expiration_date=item.expiration_date,
        notes=item.notes,
        added_date=item.added_date,
        days_until_expiry=item.days_until_expiry,
        expiry_status=item.expiry_status,
    )

