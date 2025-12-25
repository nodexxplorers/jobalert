# backend/app/config.py

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App
    APP_NAME: str = "X Job Bot"
    DEBUG: bool = True
    ENVIRONMENT: str 
    
    # Database (Supabase PostgreSQL)
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email (Gmail SMTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    
    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    
    # CORS
    FRONTEND_URL: str = "https://jobalert-peach.vercel.app"
    # X OAuth
    X_CLIENT_ID: str
    X_CLIENT_SECRET: str
    X_CALLBACK_URL: str = "https://jobalert-o93o.onrender.com"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()