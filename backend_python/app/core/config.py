"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "metersphere"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8081
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/metersphere?charset=utf8mb4"
    DATABASE_POOL_SIZE: int = 100
    DATABASE_POOL_MIN_SIZE: int = 10
    DATABASE_POOL_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 1800
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    SESSION_TIMEOUT: int = 43200  # seconds
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_GROUP_ID: str = "metersphere_group_id"
    KAFKA_MAX_REQUEST_SIZE: int = 1073741824  # 1GB
    KAFKA_BATCH_SIZE: int = 16384
    
    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_BUCKET: str = "metersphere"
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 1024 * 1024 * 1024  # 1GB
    BATCH_DOWNLOAD_MAX: str = "600MB"
    
    # JMeter
    JMETER_HOME: str = "/opt/jmeter"
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Internationalization
    DEFAULT_LOCALE: str = "zh_CN"
    SUPPORTED_LOCALES: List[str] = ["zh_CN", "zh_TW", "en_US"]
    
    # Quartz (Task Scheduler)
    QUARTZ_ENABLED: bool = True
    QUARTZ_THREAD_COUNT: int = 10
    
    # AI Configuration
    AI_ENABLED: bool = False
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()

