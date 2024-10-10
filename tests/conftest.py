import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from app import app, get_database_session
from models.user import Base
from database import get_engine
import os 
from dotenv import load_dotenv

load_dotenv()

# Database credentials
TEST_USER = os.getenv("MYSQL_USER")
TEST_PASSWORD = os.getenv("MYSQL_PASSWORD")
TEST_HOST = os.getenv("MYSQL_HOST")
TEST_PORT = os.getenv("MYSQL_PORT")
TEST_DATABASE = os.getenv("TEST_MYSQL_DATABASE")

print("DEBUG:", TEST_USER, TEST_DATABASE)

# Setup test database
TEST_DB_URL = f"mysql+pymysql://{TEST_USER}:{TEST_PASSWORD}@{TEST_HOST}:{TEST_PORT}/{TEST_DATABASE}"

engine = create_engine(TEST_DB_URL)
if not database_exists(engine.url):
    create_database(engine.url)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# fixture for db creation
@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# fixture for db session
@pytest.fixture(scope="function")
def db_session(test_db):
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

# fixture for db client
@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_database_session] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()