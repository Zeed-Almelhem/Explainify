from typing import List
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Explainify"
    API_V1_STR: str = "/api/v1"
    
    # Security
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",  # Default Vite dev server
        "http://localhost:5174",  # Alternative port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ]
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./explainify.db")
    
    # Storage
    MODEL_STORAGE_PATH: str = os.getenv("MODEL_STORAGE_PATH", "./storage/models")
    DATASET_STORAGE_PATH: str = os.getenv("DATASET_STORAGE_PATH", "./storage/datasets")
    
    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))

settings = Settings()
