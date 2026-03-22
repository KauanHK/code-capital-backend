import uuid

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_register_returns_bearer_token() -> None:
    username = f"register_{uuid.uuid4().hex[:8]}"
    response = client.post(
        "/auth/register",
        json={"username": username, "password": "Password123!"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert data["access_token"]


def test_login_returns_token_for_valid_credentials() -> None:
    username = f"login_{uuid.uuid4().hex[:8]}"
    register_response = client.post(
        "/auth/register",
        json={"username": username, "password": "Password123!"},
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={"username": username, "password": "Password123!"},
    )

    assert login_response.status_code == 200
    data = login_response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]


def test_login_rejects_invalid_password() -> None:
    username = f"invalid_{uuid.uuid4().hex[:8]}"
    register_response = client.post(
        "/auth/register",
        json={"username": username, "password": "Password123!"},
    )
    assert register_response.status_code == 201

    response = client.post(
        "/auth/login",
        json={"username": username, "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_protected_endpoint_requires_authentication() -> None:
    response = client.get("/clients")
    assert response.status_code == 401
