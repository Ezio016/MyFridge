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
    Base.metadata.create_all(bind=engine)
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


@app.get("/api/health")
def health_check():
    """API health check."""
    return {"status": "ok"}

