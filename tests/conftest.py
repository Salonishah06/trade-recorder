
import os

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app import models


# Load environment variables.
load_dotenv()

# Read the dedicated test database URL.
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    raise ValueError("TEST_DATABASE_URL is not configured")


# Create a separate SQLAlchemy engine for testing.
test_engine = create_engine(TEST_DATABASE_URL)

# Create database sessions for individual tests.
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Create database tables before the test suite runs
    and remove them after the suite finishes.
    """

    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.fixture
def db_session():
    """
    Provide an isolated database session for each test.

    Clean up test records after each test, including
    records committed by the service.
    """

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.rollback()

        # Delete records in dependency-safe order.
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())

        db.commit()
        db.close()
