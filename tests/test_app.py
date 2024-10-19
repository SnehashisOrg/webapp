import pytest
from fastapi import status
from models.user import User
import bcrypt
from datetime import datetime

"""
/healthz endpoint unit tests
"""
def test_healthcheck(client):
    response = client.get("/healthz")
    assert response.status_code == status.HTTP_200_OK

def test_healthcheck_with_query_params(client):
    response = client.get("/healthz?param=value")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_healthcheck_post(client):
    response = client.post("/healthz")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

def test_healthcheck_put(client):
    response = client.put("/healthz")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

def test_healthcheck_head(client):
    response = client.head("/healthz")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

def test_healthcheck_options(client):
    response = client.options("/healthz")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

def test_healthcheck_patch(client):
    response = client.patch("/healthz")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

def test_healthcheck_delete(client):
    response = client.delete("/healthz")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

"""
User API endpoints unit tests
"""
def test_create_user(client, db_session):
    user_data = {
        "email": "test@example.com",
        "password": "testpassword",
        "first_name": "Test",
        "last_name": "User"
    }
    response = client.post("/v2/user", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["email"] == "test@example.com"

    user = db_session.query(User).filter(User.email == "test@example.com").first()
    assert user is not None
    assert user.first_name == "Test"
    assert user.last_name == "User"

def test_create_user_invalid_name(client):
    user_data = {
        "email": "test2@example.com",
        "password": "testpassword",
        "first_name": "Test123",
        "last_name": "User"
    }
    response = client.post("/v2/user", json=user_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_create_duplicate_user(client, db_session):
    user_data = {
        "email": "duplicate@example.com",
        "password": "testpassword",
        "first_name": "Duplicate",
        "last_name": "User"
    }
    client.post("/v2/user", json=user_data)
    response = client.post("/v2/user", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_get_user(client, db_session):
    user_data = {
        "email": "getuser@example.com",
        "password": "testpassword",
        "first_name": "Get",
        "last_name": "User"
    }
    
    test_user_created = client.post("/v2/user", json=user_data)

    assert test_user_created.json()['first_name'] == "Get"
    assert test_user_created.json()["email"] == "getuser@example.com"

    response = client.get("/v2/user/self", auth=("getuser@example.com", "testpassword"))
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == "getuser@example.com"

def test_get_user_unauthorized(client):
    response = client.get("/v2/user/self")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_update_user(client, db_session):
    user_data = {
        "email": "updateuser@example.com",
        "password": "testpassword",
        "first_name": "Update",
        "last_name": "User"
    }
    client.post("/v2/user", json=user_data)

    update_data = {
        "email": "updateuser@example.com",
        "first_name": "UpdatedName",
        "last_name": "UpdatedUser"
    }
    response = client.put("/v2/user/self", json=update_data, auth=("updateuser@example.com", "testpassword"))
    assert response.status_code == status.HTTP_204_NO_CONTENT

    user = db_session.query(User).filter(User.email == "updateuser@example.com").first()
    assert user.first_name == "UpdatedName"
    assert user.last_name == "UpdatedUser"

def test_update_user_email(client):
    user_data = {
        "email": "noupdate@example.com",
        "password": "testpassword",
        "first_name": "No",
        "last_name": "Update"
    }
    client.post("/v2/user", json=user_data)

    update_data = {
        "email": "newupdate@example.com",
        "first_name": "No",
        "last_name": "Update"
    }
    response = client.put("/v2/user/self", json=update_data, auth=("noupdate@example.com", "testpassword"))
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_authenticate(client, db_session):
    user_data = {
        "email": "auth@example.com",
        "password": "testpassword",
        "first_name": "Auth",
        "last_name": "User"
    }
    client.post("/v2/user", json=user_data)

    response = client.get("/v2/user/self", auth=("auth@example.com", "testpassword"))
    assert response.status_code == status.HTTP_200_OK

def test_password_hashing(client, db_session):
    user_data = {
        "email": "hash@example.com",
        "password": "testpassword",
        "first_name": "Hash",
        "last_name": "User"
    }
    client.post("/v2/user", json=user_data)

    user = db_session.query(User).filter(User.email == "hash@example.com").first()
    assert bcrypt.checkpw("testpassword".encode('utf-8'), user.password.encode('utf-8'))