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

@pytest.fixture(autouse=True, scope="session")
def configure_service_paths():
    """Configure Python path to include all service directories for proper imports during testing."""
    import sys
    import os
    # Get the root directory of the project (parent of tests directory)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Define service directories to add to the path
    service_dirs = [
        os.path.join(project_root, 'ai-service'),
        os.path.join(project_root, 'api-gateway'),
        os.path.join(project_root, 'workflow-service'),
        os.path.join(project_root, 'shared')
    ]
    
    # Add each service directory to the beginning of sys.path if not already there
    for service_dir in service_dirs:
        if service_dir not in sys.path:
            sys.path.insert(0, service_dir)
    
    # Update PYTHONPATH environment variable
    python_path = ':'.join(service_dirs) + ':' + os.environ.get('PYTHONPATH', '')
    os.environ['PYTHONPATH'] = python_path
    
    print(f"Test environment configured. PYTHONPATH: {python_path}")
    return

@pytest.fixture(scope="session")
def test_database_url():
    """Provide test database URL."""
    return os.getenv("TEST_DATABASE_URL", "postgresql://test:test@localhost:5432/test_db")

@pytest.fixture(scope="session")
def redis_url():
    """Provide Redis URL for testing."""
    return os.getenv("REDIS_URL", "redis://localhost:6379/1")
