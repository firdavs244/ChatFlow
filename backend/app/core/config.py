"""
ChatFlow - Application Configuration
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "ChatFlow"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production"

    # Database
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "chatflow"
    POSTGRES_PASSWORD: str = "chatflow"
    POSTGRES_DB: str = "chatflow_db"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def SYNC_DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0

    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # JWT
    JWT_SECRET_KEY: str = "jwt-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # MinIO
    MINIO_HOST: str = "localhost"
    MINIO_PORT: int = 9000
    MINIO_ROOT_USER: str = "minioadmin"
    MINIO_ROOT_PASSWORD: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "chatflow-files"

    @property
    def MINIO_ENDPOINT(self) -> str:
        return f"{self.MINIO_HOST}:{self.MINIO_PORT}"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # File Upload
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_FILE_TYPES: str = "image/jpeg,image/png,image/gif,image/webp,video/mp4,video/webm,audio/mpeg,audio/wav,application/pdf,application/zip"

    @property
    def ALLOWED_FILE_TYPES_LIST(self) -> List[str]:
        return self.ALLOWED_FILE_TYPES.split(",")

    @property
    def MAX_FILE_SIZE_BYTES(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:80",
        "http://localhost:3000",
        "http://127.0.0.1",
        "http://127.0.0.1:80",
        "http://127.0.0.1:3000",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()

