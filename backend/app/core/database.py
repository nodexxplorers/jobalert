# backend/app/core/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from app.config import settings

# For Supabase, use SSL and proper pool settings
engine = create_engine(
    settings.DATABASE_URL,
    # Connection pool settings
    pool_pre_ping=True,  # Test connections before using them
    pool_size=5,  # Number of connections to keep in pool
    max_overflow=10,  # Extra connections beyond pool_size
    pool_recycle=300,  # Recycle connections every 5 mins (Supabase closes idle ones)
    pool_timeout=30,  # Timeout for wait to get connection from pool
    
    # Logging
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Prevents lazy loading issues
)

Base = declarative_base()

def get_db():
    """Dependency for database sessions in FastAPI endpoints"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()