# test/unit/domain/models/test_users.py
from models.user import UsuarioModel, EstadoUsuario
from db import db

def _mark_verified(client, user_id: str):
    """Marca al usuario como VERIFICADO directamente en la BD (sin webhook)."""
    with client.application.app_context():
        u = UsuarioModel.query.get(user_id)
        assert u is not None
        u.status = EstadoUsuario.VERIFICADO
        db.session.commit()

def test_user_ping(client):
    response = client.get("/users/ping")
    assert response.status_code == 200
    assert response.json == {"message": "Pong"}

def test_user_count_empty(client):
    response = client.get("/users/count")
    assert response.status_code == 200
    assert response.json["count"] == 0

def test_create_user_success(client):
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "123456",
        "dni": "12345678",
        "fullName": "Test User",
        "phoneNumber": "123456789"
    }
    response = client.post("/users", json=data)
    assert response.status_code == 201
    assert response.json["username"] == "testuser"
    assert "createdAt" in response.json
    assert "id" in response.json

def test_create_user_missing_field(client):
    data = {
        "username": "user2",
        "password": "123456",
        "dni": "123",
        "fullName": "User Two",
        "phoneNumber": "123456"
    }
    response = client.post("/users", json=data)
    # Tu error handler mapea 422 -> 400
    assert response.status_code == 400

def test_create_user_duplicate_username(client):
    data = {
        "username": "testuser",
        "email": "a@example.com",
        "password": "123456",
        "dni": "1111",
        "fullName": "A User",
        "phoneNumber": "1111"
    }
    client.post("/users", json=data)
    data2 = {
        "username": "testuser",
        "email": "b@example.com",
        "password": "123456",
        "dni": "2222",
        "fullName": "B User",
        "phoneNumber": "2222"
    }
    response = client.post("/users", json=data2)
    assert response.status_code == 412
    assert "Username already exists" in response.json["message"]

def test_create_user_duplicate_email(client):
    data1 = {
        "username": "user1",
        "email": "dup@example.com",
        "password": "123",
        "dni": "1111",
        "fullName": "User 1",
        "phoneNumber": "1111"
    }
    client.post("/users", json=data1)
    data2 = {
        "username": "user2",
        "email": "dup@example.com",
        "password": "123",
        "dni": "2222",
        "fullName": "User 2",
        "phoneNumber": "2222"
    }
    response = client.post("/users", json=data2)
    assert response.status_code == 412
    assert "Email already exists" in response.json["message"]

def test_auth_user_success_after_webhook(client, monkeypatch):
    # 1) Crear usuario (queda POR_VERIFICAR)
    data = {
        "username": "authuser",
        "email": "auth@example.com",
        "password": "pass123",
        "dni": "123",
        "fullName": "Auth User",
        "phoneNumber": "123456"
    }
    create_resp = client.post("/users", json=data)
    assert create_resp.status_code == 201
    user_id = create_resp.json["id"]

    # 2) Marcar VERIFICADO directamente (sin webhook/TrueNative)
    _mark_verified(client, user_id)

    # 3) Autenticación exitosa
    auth_data = {"username": "authuser", "password": "pass123"}
    response = client.post("/users/auth", json=auth_data)
    assert response.status_code == 200
    assert "token" in response.json

def test_auth_user_invalid_password(client):
    data = {
        "username": "authuser2",
        "email": "auth2@example.com",
        "password": "pass123",
        "dni": "1234",
        "fullName": "Auth User2",
        "phoneNumber": "123456"
    }
    create_resp = client.post("/users", json=data)
    assert create_resp.status_code == 201

    # Marcar VERIFICADO directo para permitir flujo de auth
    user_id = create_resp.json["id"]
    _mark_verified(client, user_id)

    auth_data = {"username": "authuser2", "password": "wrongpass"}
    response = client.post("/users/auth", json=auth_data)
    assert response.status_code == 404  # por diseño actual

def test_user_me_success(client):
    # Crear + marcar verificado + auth
    data = {
        "username": "meuser",
        "email": "me@example.com",
        "password": "passme",
        "dni": "5678",
        "fullName": "Me User",
        "phoneNumber": "5678"
    }
    create_resp = client.post("/users", json=data)
    user_id = create_resp.json["id"]

    _mark_verified(client, user_id)

    auth_response = client.post("/users/auth", json={"username": "meuser", "password": "passme"})
    token = auth_response.json["token"]
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

def test_user_me_missing_token(client):
    response = client.get("/users/me")
    assert response.status_code == 403

def test_user_me_invalid_token(client):
    response = client.get("/users/me", headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 401

def test_user_count(client):
    client.post("/users", json={
        "username": "count1", "email": "c1@example.com", "password": "123",
        "dni":"1","fullName":"Count1","phoneNumber":"1111"
    })
    client.post("/users", json={
        "username": "count2", "email": "c2@example.com", "password": "123",
        "dni":"2","fullName":"Count2","phoneNumber":"2222"
    })
    response = client.get("/users/count")
    assert response.status_code == 200
    assert response.json["count"] >= 2

def test_user_reset(client):
    client.post("/users", json={
        "username": "resetuser", "email": "reset@example.com", "password": "123",
        "dni":"3","fullName":"Reset User","phoneNumber":"3333"
    })
    response = client.post("/users/reset")
    assert response.status_code == 200
    assert "eliminados" in response.json["msg"].lower()
    count_response = client.get("/users/count")
    assert count_response.json["count"] == 0
