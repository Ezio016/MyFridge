"""Database configuration and session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./myfridge.db")

# Handle SQLite-specific settings
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL connection with pooling
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=5,         # Number of permanent connections
        max_overflow=10      # Extra connections if needed
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

