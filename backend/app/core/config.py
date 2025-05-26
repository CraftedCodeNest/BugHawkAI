# backend/app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    OPENAI_API_KEY: Optional[str] = None # Use Optional[str] to allow it to be None if not set

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / '.env',  # Points to BugHawkAI/.env
        extra="ignore" # Ignore other env vars not explicitly defined
    )

settings = Settings()