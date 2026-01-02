"""Routes package."""
from .inventory import router as inventory_router
from .chat import router as chat_router

__all__ = ["inventory_router", "chat_router"]

