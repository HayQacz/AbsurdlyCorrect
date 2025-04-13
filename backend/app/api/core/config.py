# file: app/core/config.py

import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Absurdly Correct API"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://absurdly:correct@db:5432/absurdly_db")
    ALLOWED_ORIGINS: list[str] = ["*"]

settings = Settings()
