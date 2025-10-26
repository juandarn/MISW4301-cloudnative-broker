# test/unit/domain/conftest.py
import os
import pytest
from app import create_app
from db import db

@pytest.fixture
def client():
    # Vars mínimas; no usamos TrueNative
    os.environ["SECRET_TOKEN"] = "mysupersecrettoken123"
    os.environ["PUBLIC_BASE_URL"] = "http://localhost:5000"
    os.environ["DATABASE_URI"] = "sqlite:///:memory:"

    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()

    client = app.test_client()
    yield client

    with app.app_context():
        db.drop_all()
