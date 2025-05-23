import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.main import app
from sqlalchemy.orm import sessionmaker, scoped_session
from app.database import DATABASE_URL
from asyncio import current_task

# ✅ Create an async test engine
async_engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Use async_scoped_session to avoid greenlet issues
async_session_factory = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

TestingSessionLocal = async_scoped_session(async_session_factory, scopefunc=current_task)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the event loop for the entire session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close() 


@pytest.fixture(scope="session")
async def db_session():
    """Fixture to provide an async database session."""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()  # Rollback after tests



@pytest.fixture(scope="function")
async def test_client():
    """Create a new test client with FastAPI."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        yield client
