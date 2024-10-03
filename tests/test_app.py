import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import app, get_database_session
from models.user import User, Base
from database import get_engine

TEST_DB_URL = f"mysql+pymysql://test:test@localhost/testdb"

engine = create_engine(TEST_DB_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_database_session] = override_get_db

client = TestClient(app)

def test_create_user():
    user_data = {
        "email": "test@example.com",
        "password": "testpassword",
        "firstname": "Test",
        "lastname": "User"
    }

    response = client.post("/v1/user", json=user_data)
    assert response.status_code == 201