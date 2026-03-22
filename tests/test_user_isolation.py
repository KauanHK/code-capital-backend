import uuid

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _register_and_get_headers() -> dict[str, str]:
    username = f"u_{uuid.uuid4().hex[:8]}"
    number = f"num_{uuid.uuid4().hex[:8]}"
    response = client.post(
        "/auth/register",
        json={"username": username, "number": number, "password": "Password123!"},
    )
    assert response.status_code == 201
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _create_category(headers: dict[str, str], name: str) -> str:
    response = client.post("/categories", json={"name": name}, headers=headers)
    assert response.status_code == 201
    return response.json()["id"]


def _create_service(headers: dict[str, str], category_id: str, name: str) -> str:
    response = client.post(
        "/services",
        json={"name": name, "category_id": category_id},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()["id"]


def _create_client(headers: dict[str, str], name: str) -> str:
    suffix = uuid.uuid4().hex[:8]
    response = client.post(
        "/clients",
        json={
            "name": name,
            "cpf_cnpj": f"{suffix}0001",
            "email": f"{suffix}@example.com",
            "phone": "11999999999",
            "type": "pj",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()["id"]


def _create_transaction(headers: dict[str, str], service_id: str, client_id: str) -> str:
    response = client.post(
        "/transactions",
        json={
            "client_id": client_id,
            "service_id": service_id,
            "is_expense": False,
            "is_personal": False,
            "pjpf": "pj",
            "amount": "100.00",
            "description": "isolation",
            "status": "pending",
            "payment_method": "pix",
            "transaction_date": "2026-03-22",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_user_cannot_access_other_users_client() -> None:
    owner_headers = _register_and_get_headers()
    other_headers = _register_and_get_headers()

    client_id = _create_client(owner_headers, "Owner Client")
    response = client.get(f"/clients/{client_id}", headers=other_headers)

    assert response.status_code == 404


def test_user_cannot_access_other_users_transaction() -> None:
    owner_headers = _register_and_get_headers()
    other_headers = _register_and_get_headers()

    category_id = _create_category(owner_headers, f"cat-{uuid.uuid4().hex[:6]}")
    service_id = _create_service(owner_headers, category_id, f"svc-{uuid.uuid4().hex[:6]}")
    owner_client_id = _create_client(owner_headers, "Owner Tx Client")
    transaction_id = _create_transaction(owner_headers, service_id, owner_client_id)

    response = client.get(f"/transactions/{transaction_id}", headers=other_headers)

    assert response.status_code == 404


def test_user_cannot_create_transaction_with_other_users_service() -> None:
    owner_headers = _register_and_get_headers()
    other_headers = _register_and_get_headers()

    category_id = _create_category(owner_headers, f"cat-{uuid.uuid4().hex[:6]}")
    service_id = _create_service(owner_headers, category_id, f"svc-{uuid.uuid4().hex[:6]}")
    other_client_id = _create_client(other_headers, "Other Client")

    response = client.post(
        "/transactions",
        json={
            "client_id": other_client_id,
            "service_id": service_id,
            "is_expense": False,
            "is_personal": False,
            "pjpf": "pj",
            "amount": "100.00",
            "description": "invalid relationship",
            "status": "pending",
            "payment_method": "pix",
            "transaction_date": "2026-03-22",
        },
        headers=other_headers,
    )

    assert response.status_code == 404
