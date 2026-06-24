"""FastAPI application entry point."""
import os
from dotenv import load_dotenv
load_dotenv()  # Load .env file

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import engine, Base
from .routes import inventory_router, chat_router, recipes_router
from .routers.recipe_lab import router as recipe_lab_router
from .routers.auth import router as auth_router
from .routers.user import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - create tables on startup."""
    import os
    db_url = os.getenv("DATABASE_URL", "sqlite:///./myfridge.db")
    print(f"🔌 Database URL: {db_url[:50]}...")  # Log database type
    print(f"📊 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print(f"✅ Database tables created successfully")
    yield


app = FastAPI(
    title="MyFridge API",
    description="AI-powered fridge inventory and meal planning for students",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS - allow frontend to connect
# Security: Only allow specific origins
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000"  # Development defaults
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in ALLOWED_ORIGINS],  # Whitelist only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Explicit methods
    allow_headers=["Content-Type", "Authorization"],  # Explicit headers
)

# Include routers
app.include_router(inventory_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(recipes_router, prefix="/api")
app.include_router(recipe_lab_router)  # Recipe Lab - already has /api/lab prefix
app.include_router(auth_router)  # Auth - already has /api/auth prefix
app.include_router(user_router)  # User - already has /api/user prefix


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": "MyFridge API",
        "version": "0.1.0"
    }


@app.get("/debug/db-status")
def db_status():
    """Debug endpoint to check database status."""
    import os
    from sqlalchemy import inspect
    
    db_url = os.getenv("DATABASE_URL", "sqlite:///./myfridge.db")
    db_type = "PostgreSQL" if db_url.startswith("postgres") else "SQLite"
    
    # Check tables
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    # Try to count items
    from .database import SessionLocal
    from .models import FridgeItem
    db = SessionLocal()
    try:
        item_count = db.query(FridgeItem).count()
    except Exception as e:
        item_count = f"Error: {str(e)}"
    finally:
        db.close()
    
    return {
        "database_type": db_type,
        "database_url_prefix": db_url[:30] + "...",
        "tables": tables,
        "fridge_item_count": item_count
    }


@app.get("/api/health")
def health_check():
    """API health check."""
    return {"status": "ok"}

