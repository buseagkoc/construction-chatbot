from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Config - replace with your key in .env
    OPENAI_API_KEY: str
    
    # Storage settings - these defaults work well locally
    REDIS_URL: str = "redis://localhost:6379"
    VECTOR_DB_PATH: str = "db/vector_store"
    
    # I found these values work well for most construction docs
    # Adjust if you're processing a lot more documents
    BATCH_SIZE: int = 10
    MAX_CONCURRENT_CALLS: int = 5
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()