from typing import Optional
from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "servidores_db"
    environment: str = "development"
    
    @field_validator("mongodb_url")
    @classmethod
    def validate_mongodb_url(cls, v):
        if not v.startswith("mongodb://") and not v.startswith("mongodb+srv://"):
            raise ValueError("MongoDB URL deve começar com mongodb:// ou mongodb+srv://")
        return v
    
    model_config = {
        "env_file": ".env",
        "extra": "ignore"  # Ignora campos extras
    }

settings = Settings()