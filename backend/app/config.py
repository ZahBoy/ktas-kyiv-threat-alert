import os
from typing import Optional
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application configuration settings."""
    app_name: str = "Kyiv Threat Alert System (KTAS)"
    version: str = "1.0.0"
    debug: bool = Field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    mock_mode: bool = Field(default_factory=lambda: os.getenv("MOCK_MODE", "true").lower() == "true")
    
    # Telegram MTProto Credentials (Production)
    telegram_api_id: Optional[int] = Field(
        default_factory=lambda: int(os.getenv("TELEGRAM_API_ID")) if os.getenv("TELEGRAM_API_ID") else None
    )
    telegram_api_hash: Optional[str] = Field(
        default_factory=lambda: os.getenv("TELEGRAM_API_HASH")
    )
    telegram_channels: list[str] = Field(
        default_factory=lambda: os.getenv("TELEGRAM_CHANNELS", "@monitor_war,@vanek_nikolaev,@kpszsu").split(",")
    )
    
    # Firebase Cloud Messaging
    fcm_credentials_path: Optional[str] = Field(
        default_factory=lambda: os.getenv("FCM_CREDENTIALS_PATH")
    )
    
    # Server configuration
    host: str = Field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = Field(default_factory=lambda: int(os.getenv("PORT", "8000")))


settings = Settings()
