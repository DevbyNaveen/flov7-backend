import pytest
import asyncio
from typing import AsyncGenerator
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_client():
    """Create a test client for FastAPI applications."""
    from httpx import AsyncClient
    # This will be used by individual service tests
    # Each service can override this fixture
    pass

@pytest.fixture(autouse=True)
def env_setup():
    """Set up test environment variables."""
    os.environ["TESTING"] = "True"
    os.environ["DEBUG"] = "True"

@pytest.fixture(scope="session")
def test_database_url():
    """Provide test database URL."""
    return os.getenv("TEST_DATABASE_URL", "postgresql://test:test@localhost:5432/test_db")

@pytest.fixture(scope="session")
def redis_url():
    """Provide Redis URL for testing."""
    return os.getenv("REDIS_URL", "redis://localhost:6379/1")
