# backend/app/models/system_status.py

from sqlalchemy import Integer, String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base

class SystemStatus(Base):
    __tablename__ = "system_status"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    is_scraping: Mapped[bool] = mapped_column(Boolean, default=False)
    last_scrape_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    last_jobs_found: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str] = mapped_column(String, nullable=True)
    twitter_cookies: Mapped[str] = mapped_column(String, nullable=True) # Store JSON formatted cookies
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
