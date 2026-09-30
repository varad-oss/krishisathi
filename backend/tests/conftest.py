import os
import pytest
from alembic.config import Config
from alembic import command

# Force tests to use a temporary local database
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_krishisathi.db"

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Run alembic upgrade head on the test database
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    
    yield
    
    # Cleanup after tests
    if os.path.exists("test_krishisathi.db"):
        os.remove("test_krishisathi.db")
