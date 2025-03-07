import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

# Replace 'your_password' with your actual PostgreSQL password.
# DATABASE_URL = "postgresql+asyncpg://postgres:1818@localhost:5432/scalpel_db"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:1818@localhost:5432/scalpel_db")

# Create the async engine.
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Create a sessionmaker for generating AsyncSession instances.
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency to get a session in FastAPI endpoints
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session