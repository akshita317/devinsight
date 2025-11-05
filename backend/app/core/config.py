from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./devinsight.db"
    
    # GitHub
    GITHUB_TOKEN: str = ""
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    
    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None
    
    # SendGrid
    SENDGRID_API_KEY: Optional[str] = None
    FROM_EMAIL: Optional[str] = "noreply@devinsight.com"
    
    # Application
    SECRET_KEY: str = "dev-secret-key"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

settings = Settings()