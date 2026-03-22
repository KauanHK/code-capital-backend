import uuid

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _auth_headers() -> dict[str, str]:
    suffix = uuid.uuid4().hex[:8]
    response = client.post(
        "/auth/register",
        json={"username": f"user_{suffix}", "number": f"num_{suffix}", "password": "Password123!"},
    )
    assert response.status_code == 201
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _create_category(name: str, headers: dict[str, str]) -> str:
    response = client.post("/categories", json={"name": name}, headers=headers)
    assert response.status_code == 201
    return response.json()["id"]


def _create_service(name: str, category_id: str, headers: dict[str, str]) -> str:
    response = client.post(
        "/services",
        json={"name": name, "category_id": category_id},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()["id"]


def _create_client(name: str, headers: dict[str, str]) -> str:
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


def _create_transaction(
    service_id: str,
    headers: dict[str, str],
    *,
    client_id: str | None,
    status: str,
    is_expense: bool,
    is_personal: bool,
    pjpf: str | None,
) -> str:
    response = client.post(
        "/transactions",
        json={
            "client_id": client_id,
            "service_id": service_id,
            "is_expense": is_expense,
            "is_personal": is_personal,
            "pjpf": pjpf,
            "amount": "150.00",
            "description": "transaction test",
            "status": status,
            "payment_method": "pix",
            "transaction_date": "2026-03-22",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_list_transactions_filters_by_status() -> None:
    headers = _auth_headers()
    suffix = uuid.uuid4().hex[:8]
    category_id = _create_category(f"cat-status-{suffix}", headers)
    service_id = _create_service(f"service-status-{suffix}", category_id, headers)
    client_id = _create_client(f"client-status-{suffix}", headers)

    pending_id = _create_transaction(
        service_id,
        headers,
        client_id=client_id,
        status="pending",
        is_expense=True,
        is_personal=False,
        pjpf="pj",
    )
    paid_id = _create_transaction(
        service_id,
        headers,
        client_id=client_id,
        status="paid",
        is_expense=True,
        is_personal=False,
        pjpf="pj",
    )

    response = client.get("/transactions", params={"status": "pending"}, headers=headers)

    assert response.status_code == 200
    data = response.json()
    ids = {item["id"] for item in data}

    assert pending_id in ids
    assert paid_id not in ids
    assert all(item["status"] == "pending" for item in data)


def test_list_transactions_filters_by_boolean_fields() -> None:
    headers = _auth_headers()
    suffix = uuid.uuid4().hex[:8]
    category_id = _create_category(f"cat-bool-{suffix}", headers)
    service_id = _create_service(f"service-bool-{suffix}", category_id, headers)
    client_id = _create_client(f"client-bool-{suffix}", headers)

    wanted_id = _create_transaction(
        service_id,
        headers,
        client_id=client_id,
        status="pending",
        is_expense=False,
        is_personal=True,
        pjpf="pj",
    )
    skipped_id = _create_transaction(
        service_id,
        headers,
        client_id=client_id,
        status="pending",
        is_expense=True,
        is_personal=False,
        pjpf="pj",
    )

    response = client.get(
        "/transactions",
        params={"is_expense": "false", "is_personal": "true"},
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    ids = {item["id"] for item in data}

    assert wanted_id in ids
    assert skipped_id not in ids
    assert all(item["is_expense"] is False and item["is_personal"] is True for item in data)


def test_list_transactions_filters_by_pjpf_client_and_service() -> None:
    headers = _auth_headers()
    suffix = uuid.uuid4().hex[:8]
    category_id = _create_category(f"cat-combined-{suffix}", headers)
    service_a_id = _create_service(f"service-a-{suffix}", category_id, headers)
    service_b_id = _create_service(f"service-b-{suffix}", category_id, headers)
    client_a_id = _create_client(f"client-a-{suffix}", headers)
    client_b_id = _create_client(f"client-b-{suffix}", headers)

    wanted_id = _create_transaction(
        service_a_id,
        headers,
        client_id=client_a_id,
        status="pending",
        is_expense=False,
        is_personal=False,
        pjpf="pj",
    )
    _create_transaction(
        service_b_id,
        headers,
        client_id=client_a_id,
        status="pending",
        is_expense=False,
        is_personal=False,
        pjpf="pj",
    )
    _create_transaction(
        service_a_id,
        headers,
        client_id=client_b_id,
        status="pending",
        is_expense=False,
        is_personal=False,
        pjpf="pf",
    )

    response = client.get(
        "/transactions",
        params={
            "pjpf": "pj",
            "client_id": client_a_id,
            "service_id": service_a_id,
        },
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    ids = {item["id"] for item in data}

    assert wanted_id in ids
    assert all(item["pjpf"] == "pj" for item in data)
    assert all(item["client_id"] == client_a_id for item in data)
    assert all(item["service_id"] == service_a_id for item in data)


def test_list_transactions_with_non_matching_filter_returns_empty_list() -> None:
    headers = _auth_headers()
    response = client.get(
        "/transactions",
        params={"client_id": str(uuid.uuid4()), "service_id": str(uuid.uuid4())},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == []


def test_list_transactions_rejects_invalid_query_params() -> None:
    headers = _auth_headers()
    invalid_status_response = client.get("/transactions", params={"status": "done"}, headers=headers)
    invalid_client_id_response = client.get(
        "/transactions", params={"client_id": "not-a-uuid"}, headers=headers
    )

    assert invalid_status_response.status_code == 422
    assert invalid_client_id_response.status_code == 422
