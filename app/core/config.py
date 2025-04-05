from typing import List
from pydantic import BaseSettings, AnyHttpUrl
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Explainify"
    API_V1_STR: str = "/api/v1"
    
    # Security
    ALLOWED_ORIGINS: List[AnyHttpUrl] = []
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./explainify.db")
    
    # Storage
    MODEL_STORAGE_PATH: str = os.getenv("MODEL_STORAGE_PATH", "./storage/models")
    DATASET_STORAGE_PATH: str = os.getenv("DATASET_STORAGE_PATH", "./storage/datasets")
    
    # Redis & Celery
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Compute Resources
    MAX_EXPLANATION_TIMEOUT: int = int(os.getenv("MAX_EXPLANATION_TIMEOUT", "3600"))
    MAX_MEMORY_LIMIT: int = int(os.getenv("MAX_MEMORY_LIMIT", "8192"))  # MB
    
    class Config:
        case_sensitive = True

settings = Settings()
