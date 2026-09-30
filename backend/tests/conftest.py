"""Test database isolation.

Tests delete rows, so they never touch the database in DATABASE_URL (which may also come from backend/.env).
They use TEST_DATABASE_URL when set (CI points it at PostgreSQL), otherwise a throwaway SQLite file.
This runs before any test module imports `config`, so every module sees the same URL.
"""
import os
import tempfile

import pytest
from alembic import command
from alembic.config import Config

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_tmp_dir = None if os.environ.get("TEST_DATABASE_URL") else tempfile.mkdtemp(prefix="krishisathi-test-")
os.environ["DATABASE_URL"] = os.environ.get("TEST_DATABASE_URL") or f"sqlite+aiosqlite:///{_tmp_dir}/test.db"


@pytest.fixture(scope="session", autouse=True)
def migrated_test_db():
    command.upgrade(Config(os.path.join(BACKEND_DIR, "alembic.ini")), "head")
    yield
    if _tmp_dir:
        import shutil
        shutil.rmtree(_tmp_dir, ignore_errors=True)
