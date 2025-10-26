import json
import uuid
from models.offer import Size, OfferModel
from db import db

def test_ping(client):
    response = client.get("/offers/ping")
    assert response.status_code == 200
    assert response.json == {"msg": "pong"}

def test_create_offer_success(client):
    data = {
        "postId": str(uuid.uuid4()),
        "userId": str(uuid.uuid4()),
        "description": "Test offer",
        "size": "SMALL",
        "fragile": False,
        "offer": 100
    }

    response = client.post("/offers", json=data)
    assert response.status_code == 201


def test_create_offer_invalid_size(client):
    data = {
        "postId": str(uuid.uuid4()),
        "userId": str(uuid.uuid4()),
        "description": "Invalid size offer",
        "size": "EXTRA",
        "fragile": False,
        "offer": 50
    }
    response = client.post("/offers", json=data)
    assert response.status_code == 412
    assert "Invalid size value" in response.json["message"]

def test_create_offer_negative_value(client):
    data = {
        "postId": str(uuid.uuid4()),
        "userId": str(uuid.uuid4()),
        "description": "Negative offer",
        "size": "MEDIUM",
        "fragile": True,
        "offer": -10
    }
    response = client.post("/offers", json=data)
    assert response.status_code == 412
    assert "Invalid offer value" in response.json["message"]

def test_get_offers_list(client):
    # Crear una oferta primero
    offer = OfferModel(
        postId=str(uuid.uuid4()),
        userId=str(uuid.uuid4()),
        description="List test",
        size=Size.LARGE,
        fragile=True,
        offer=200
    )
    db.session.add(offer)
    db.session.commit()

    response = client.get("/offers")
    assert response.status_code == 200
    assert any(o["description"] == "List test" for o in response.json)

def test_get_offer_by_id(client):
    offer = OfferModel(
        postId=str(uuid.uuid4()),
        userId=str(uuid.uuid4()),
        description="Get by ID",
        size=Size.MEDIUM,
        fragile=False,
        offer=150
    )
    db.session.add(offer)
    db.session.commit()

    response = client.get(f"/offers/{offer.id}")
    assert response.status_code == 200
    assert response.json["description"] == "Get by ID"

def test_get_offer_invalid_uuid(client):
    response = client.get("/offers/invalid-uuid")
    assert response.status_code == 400
    assert "Invalid offer ID" in response.json["message"]

def test_delete_offer(client):
    offer = OfferModel(
        postId=str(uuid.uuid4()),
        userId=str(uuid.uuid4()),
        description="Delete test",
        size=Size.SMALL,
        fragile=True,
        offer=75
    )
    db.session.add(offer)
    db.session.commit()

    response = client.delete(f"/offers/{offer.id}")
    assert response.status_code == 200
    assert response.json["msg"] == "la oferta fue eliminada"

def test_count_offers(client):
    db.session.query(OfferModel).delete()
    db.session.commit()

    offer1 = OfferModel(
        postId=str(uuid.uuid4()), userId=str(uuid.uuid4()),
        description="Count 1", size=Size.SMALL, fragile=False, offer=10
    )
    offer2 = OfferModel(
        postId=str(uuid.uuid4()), userId=str(uuid.uuid4()),
        description="Count 2", size=Size.MEDIUM, fragile=True, offer=20
    )
    db.session.add_all([offer1, offer2])
    db.session.commit()

    response = client.get("/offers/count")
    assert response.status_code == 200
    assert response.json["count"] == 2

def test_reset_offers(client):
    offer = OfferModel(
        postId=str(uuid.uuid4()), userId=str(uuid.uuid4()),
        description="Reset test", size=Size.LARGE, fragile=False, offer=100
    )
    db.session.add(offer)
    db.session.commit()

    response = client.post("/offers/reset")
    assert response.status_code == 200
    assert response.json["msg"] == "Todos los datos fueron eliminados"

    # Confirmar que no quedan registros
    count_response = client.get("/offers/count")
    assert count_response.json["count"] == 0
