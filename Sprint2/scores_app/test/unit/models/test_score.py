import pytest
import uuid

def test_ping(client):
    """Verifica que el servicio esté vivo"""
    response = client.get("/score/ping")
    assert response.status_code == 200
    assert response.get_json() == {"message": "Pong"}


def test_get_score_not_found(client):
    """Si no hay score para la oferta, debe devolver None"""
    oferta_id = str(uuid.uuid4())
    response = client.get(f"/score/{oferta_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["oferta_id"] == oferta_id
    assert data["utilidad"] is None


def test_post_score_and_get_it(client):
    """Crea un score y luego lo recupera"""
    oferta_id = str(uuid.uuid4())
    payload = {"oferta_id": oferta_id, "utilidad": 95}

    # Crear score
    response = client.post("/score/", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["oferta_id"] == oferta_id
    assert data["utilidad"] == 95

    # Recuperar el score creado
    response = client.get(f"/score/{oferta_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["oferta_id"] == oferta_id
    assert data["utilidad"] == 95


def test_post_multiple_scores(client):
    """Permite crear varios scores distintos"""
    scores = [
        {"oferta_id": str(uuid.uuid4()), "utilidad": 80},
        {"oferta_id": str(uuid.uuid4()), "utilidad": 70},
    ]
    for score in scores:
        r = client.post("/score/", json=score)
        assert r.status_code == 200
        data = r.get_json()
        assert data["oferta_id"] == score["oferta_id"]
        assert data["utilidad"] == score["utilidad"]


def test_reset_scores(client):
    """Después de resetear, la base queda vacía"""
    # Crear un score
    payload = {"oferta_id": str(uuid.uuid4()), "utilidad": 60}
    client.post("/score/", json=payload)

    # Resetear
    response = client.post("/score/reset")
    assert response.status_code == 200
    assert response.get_json() == {"msg": "Todos los datos fueron eliminados"}

    # Ya no debería estar el score
    oferta_id = payload["oferta_id"]
    response = client.get(f"/score/{oferta_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["utilidad"] is None
