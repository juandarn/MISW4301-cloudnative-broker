from __future__ import annotations

from models.credit_card import CardStatus, CreditCardModel


def auth_headers(token="super-secret-test"):
    return {"Authorization": f"Bearer {token}"}


def sample_payload(**overrides):
    base = {
        "userId": "user-1",
        "email": "user@example.com",
        "fullName": "Jane Doe",
        "cardNumber": "4111111111111111",
        "expirationDate": "30/12",
        "cvv": "123",
        "documentNumber": "12345678",
    }
    base.update(overrides)
    return base


def _get_dummy_services(client):
    app = client.application
    return (
        app.config["dummy_truenative_client"],
        app.config["dummy_queue_publisher"],
    )


def test_create_card_success(client):
    dummy_client, dummy_publisher = _get_dummy_services(client)

    response = client.post(
        "/credit-cards",
        json=sample_payload(),
        headers=auth_headers(),
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["userId"] == "user-1"
    assert data["status"] == CardStatus.POR_VERIFICAR.value
    assert data["lastFourDigits"] == "1111"
    assert "ruv" in data

    with client.application.app_context():
        stored = CreditCardModel.query.first()
        assert stored is not None
        assert stored.user_id == "user-1"
    assert len(dummy_client.calls) == 1
    assert len(dummy_publisher.messages) == 1


def test_create_card_requires_token(client):
    response = client.post("/credit-cards", json=sample_payload())
    assert response.status_code in {401, 403}


def test_create_card_conflict_when_duplicate(client):
    client.post(
        "/credit-cards",
        json=sample_payload(),
        headers=auth_headers(),
    )

    response = client.post(
        "/credit-cards",
        json=sample_payload(),
        headers=auth_headers(),
    )

    assert response.status_code == 409


def test_list_cards_filters_by_user(client):
    client.post(
        "/credit-cards",
        json=sample_payload(userId="user-1"),
        headers=auth_headers(),
    )
    client.post(
        "/credit-cards",
        json=sample_payload(userId="user-2", cardNumber="5555555555554444"),
        headers=auth_headers(),
    )

    response = client.get("/credit-cards", query_string={"userId": "user-1"}, headers=auth_headers())
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["userId"] == "user-1"


def test_count_endpoint(client):
    client.post(
        "/credit-cards",
        json=sample_payload(),
        headers=auth_headers(),
    )

    response = client.get("/credit-cards/count", headers=auth_headers())
    assert response.status_code == 200
    assert response.get_json()["count"] == 1


def test_ping_endpoint(client):
    response = client.get("/credit-cards/ping")
    assert response.status_code == 200
    assert response.get_json()["message"].lower() == "pong"


def test_update_status(client):
    post_resp = client.post(
        "/credit-cards",
        json=sample_payload(),
        headers=auth_headers(),
    )
    ruv = post_resp.get_json()["ruv"]

    patch_resp = client.patch(
        f"/credit-cards/ruv/{ruv}",
        json={"status": CardStatus.APROBADA.value},
        headers=auth_headers(),
    )
    assert patch_resp.status_code == 200
    assert patch_resp.get_json()["status"] == CardStatus.APROBADA.value