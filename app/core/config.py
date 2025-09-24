from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os

class BaseConfig(BaseSettings): 
    
    # MongoDB
    DB_URI: str = "mongodb://localhost:27017"
    DB_NAME: str = "seven_healer_db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    JWT_SECRET_KEY: str = "your-jwt-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SUPERUSER_ID: str = "superuser123"
    SUPERUSER_EMAIL: str = "admin@sevenhealerconsultants.in"
    SUPERUSER_PASSWORD: str = "admin123"
    
    # Email
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "atulverma2861@gmail.com"
    SMTP_PASSWORD: str = "iprs nibw chif rktr"
    
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://sevenhealerconsultants.in"
    ]

    
    # class Config:
    #     env_file = ".env"
    #     case_sensitive = True

# Create settings instance
#settings = Settings()
class DevConfig(BaseConfig):
    model_config = SettingsConfigDict(env_file="env/.env.dev", extra="ignore")


class ProdConfig(BaseConfig):
    model_config = SettingsConfigDict(env_file="env/.env.prod", extra="ignore")


configs = {"dev": DevConfig, "prod": ProdConfig}

config: BaseConfig = configs[os.environ.get("ENV", "dev").lower()]()

