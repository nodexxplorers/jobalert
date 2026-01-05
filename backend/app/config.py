# backend/app/config.py
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "X Job Bot"
    DEBUG: bool = True
    ENVIRONMENT: str

    DATABASE_URL: str

    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str

    TELEGRAM_BOT_TOKEN: Optional[str] = None

    FRONTEND_URL: str

    # X OAuth (FIXED)
    X_CLIENT_ID: Optional[str] = None
    X_CLIENT_SECRET: Optional[str] = None
    X_CALLBACK_URL: Optional[str] = None

    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_CALLBACK_URL: Optional[str] = None

    # Twitter Scraper Credentials
    TWITTER_USERNAME: Optional[str] = None
    TWITTER_PASSWORD: Optional[str] = None
    TWITTER_EMAIL: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
