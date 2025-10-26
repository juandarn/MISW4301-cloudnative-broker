from __future__ import annotations

from cards_poller import map_status, process_message
from db import db
from models.credit_card import CardStatus, CreditCardModel
from services.notifications import NotificationService


class StubConsumer:
    def __init__(self):
        self.deleted = []

    def delete_message(self, receipt_handle):
        self.deleted.append(receipt_handle)


class StubClient:
    def __init__(self, status):
        self.status = status

    def get_card_status(self, ruv):
        return 200, {"status": self.status, "issuer": "Visa"}


class StubNotifier(NotificationService):
    def __init__(self):
        self.sent = []

    def send_card_approved(self, to_email, context):  # type: ignore[override]
        self.sent.append(("APPROVED", to_email, context))

    def send_card_rejected(self, to_email, context):  # type: ignore[override]
        self.sent.append(("REJECTED", to_email, context))


def test_map_status():
    assert map_status("approved") == CardStatus.APROBADA
    assert map_status("rejected") == CardStatus.RECHAZADA
    assert map_status("pending") == CardStatus.POR_VERIFICAR
    assert map_status("unknown") is None


def test_process_message_updates_status(app):
    consumer = StubConsumer()
    client = StubClient("APPROVED")
    notifier = StubNotifier()

    with app.app_context():
        card = CreditCardModel(
            token="token",
            user_id="user",
            last_four_digits="1111",
            ruv="RUV-1",
            status=CardStatus.POR_VERIFICAR,
            fingerprint="fp",
        )
        db.session.add(card)
        db.session.commit()

    message = {"payload": {"ruv": "RUV-1", "email": "user@example.com", "fullName": "User"}, "receipt_handle": "abc"}

    process_message(app, consumer, client, notifier, message)

    with app.app_context():
        updated = CreditCardModel.query.filter_by(ruv="RUV-1").first()
        assert updated.status == CardStatus.APROBADA

    assert consumer.deleted == ["abc"]
    assert notifier.sent[0][0] == "APPROVED"
