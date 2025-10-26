import os
import uuid

import pytest

from app import create_app
from db import db


class DummyTrueNativeClient:
    def __init__(self):
        self.calls = []

    def register_card(self, payload, transaction_identifier):
        self.calls.append((payload, transaction_identifier))
        return {
            "ruv": payload.get("transactionIdentifier") or f"RUV-{transaction_identifier}",
            "cardToken": str(uuid.uuid4()),
        }


class DummyQueuePublisher:
    def __init__(self):
        self.messages = []

    def publish(self, message):
        self.messages.append(message)
        return {"MessageId": str(len(self.messages))}


@pytest.fixture
def app():
    os.environ.setdefault("SECRET_TOKEN", "super-secret-test")
    os.environ.setdefault("CARD_FINGERPRINT_PEPPER", "pepper-test")
    os.environ.setdefault("DATABASE_URI", "sqlite:///:memory:")
    os.environ.setdefault("TRUENATIVE_BASE_URL", "http://truenative.local")
    os.environ.setdefault("CARDS_QUEUE_URL", "https://sqs.local/queue")

    application = create_app(os.environ["DATABASE_URI"])
    application.config["TESTING"] = True

    from credit_cards_app.resources import credit_cards as credit_cards_resources
    # Some modules inside the app import using the package prefix ``resources``
    # instead of ``credit_cards_app.resources``. Import both to ensure our test
    # doubles are wired regardless of the import path used.
    try:  # pragma: no cover - optional dependency
        from resources import credit_cards as legacy_credit_cards_resources
    except ModuleNotFoundError:  # pragma: no cover - fallback when not installed
        legacy_credit_cards_resources = None

    dummy_client = DummyTrueNativeClient()
    dummy_publisher = DummyQueuePublisher()

    credit_cards_resources._create_client = lambda: dummy_client
    credit_cards_resources._queue_publisher = lambda: dummy_publisher

    if legacy_credit_cards_resources is not None:
        legacy_credit_cards_resources._create_client = lambda: dummy_client
        legacy_credit_cards_resources._queue_publisher = lambda: dummy_publisher

    application.config["dummy_truenative_client"] = dummy_client
    application.config["dummy_queue_publisher"] = dummy_publisher

    with application.app_context():
        db.create_all()

    yield application

    with application.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
