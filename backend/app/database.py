﻿import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Pobieramy DATABASE_URL ze zmiennych środowiskowych, domyślnie ustawiamy adres dla Dockera.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://absurdly:correct@db:5432/absurdly_db")

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)
