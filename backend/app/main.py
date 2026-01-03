"""FastAPI application entry point."""
from dotenv import load_dotenv
load_dotenv()  # Load .env file

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import engine, Base
from .routes import inventory_router, chat_router, recipes_router


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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for deployed version
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(inventory_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(recipes_router, prefix="/api")


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

