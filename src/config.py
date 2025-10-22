"""Configuration management for the Ocean Forecasting Agent."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # AWS Configuration
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    bedrock_region: str = "us-east-1"
    
    # External APIs
    copernicus_username: Optional[str] = None
    copernicus_password: Optional[str] = None
    
    # S3 Configuration
    s3_bucket_name: str = "ocean-forecast-data"
    s3_region: str = "us-east-1"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_timeout: int = 60
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()
