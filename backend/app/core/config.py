"""Application configuration."""
from functools import lru_cache
from typing import List, Optional

from pydantic import AliasChoices
from pydantic import Field
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )
    
    # App
    APP_NAME: str = "CV Research Hub"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    LOG_LEVEL: str = "info"
    SECRET_KEY: Optional[str] = None
    PUBLIC_BASE_URL: Optional[str] = None
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        validation_alias=AliasChoices("CORS_ORIGINS", "ALLOWED_ORIGINS"),
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        """Allow CORS origins to be provided as a JSON array or comma-separated string."""
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return []
            if value.startswith("["):
                return value
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("GITHUB_TOKEN", "OPENAI_API_KEY", "HUGGINGFACE_TOKEN", "GEMINI_API_KEY", mode="before")
    @classmethod
    def normalize_placeholder_secrets(cls, value):
        """Treat example placeholder secrets as unset values."""
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return None
            lowered = stripped.lower()
            if lowered.startswith("your_") and lowered.endswith(("_here", "_token_here", "_key_here")):
                return None
        return value
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/cv_research_hub"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_URL: str = "redis://localhost:6379/1"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/2"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/3"
    
    # External APIs
    GITHUB_TOKEN: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    HUGGINGFACE_TOKEN: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_FALLBACK_MODEL: Optional[str] = "gemini-2.5-flash-lite"
    GEMINI_RESULTS_PER_CATEGORY: int = 3
    GEMINI_LOOKBACK_DAYS: int = 7
    GEMINI_ENABLE_FULL_REFRESH: bool = True
    GEMINI_ENABLE_CATEGORY_REFRESH: bool = False
    GEMINI_ENABLE_MANUAL_REFRESH: bool = False
    GEMINI_MAX_RETRIES: int = 5
    GEMINI_REQUEST_DELAY_SECONDS: float = 3.0
    
    # Ingestion Settings
    ARXIV_MAX_RESULTS_PER_QUERY: int = 100
    GITHUB_MAX_REPOS_PER_QUERY: int = 50
    PAPERS_WITH_CODE_MAX_RESULTS: int = 100
    
    # Scoring Weights
    SCORE_RECENCY_WEIGHT: float = 0.25
    SCORE_CODE_WEIGHT: float = 0.20
    SCORE_SOURCE_WEIGHT: float = 0.15
    SCORE_IMPACT_WEIGHT: float = 0.25
    SCORE_CLARITY_WEIGHT: float = 0.15
    
    # Scheduling
    DAILY_INGESTION_HOUR: int = 6  # 6 AM UTC
    GITHUB_REFRESH_INTERVAL_HOURS: int = 6
    
@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
