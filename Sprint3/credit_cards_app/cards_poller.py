from __future__ import annotations

import logging
import os
import time
from typing import Any

from flask import Flask

from app import create_app
from db import db
from models.credit_card import CardIssuer, CardStatus, CreditCardModel
from services.cards_queue_consumer import CardsQueueConsumer
from services.notifications import NotificationService
from services.truenative_cards_client import TrueNativeCardsClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cards_poller")

STATUS_MAPPING = {
    "APPROVED": CardStatus.APROBADA,
    "APPROVE": CardStatus.APROBADA,
    "APPROVED_WITH_RISK": CardStatus.APROBADA,
    "REJECTED": CardStatus.RECHAZADA,
    "DECLINED": CardStatus.RECHAZADA,
    "PENDING": CardStatus.POR_VERIFICAR,
    "SENT": CardStatus.POR_VERIFICAR,
}


def create_context() -> Flask:
    database_uri = os.environ.get("DATABASE_URI")
    app = create_app(database_uri)
    return app


def map_status(value: str | None) -> CardStatus | None:
    if not value:
        return None
    upper = value.upper()
    return STATUS_MAPPING.get(upper)


def process_message(
    app: Flask,
    consumer: CardsQueueConsumer,
    client: TrueNativeCardsClient,
    notifier: NotificationService,
    message: dict[str, Any],
) -> None:
    payload = message.get("payload", {})
    receipt_handle = message.get("receipt_handle")

    ruv = payload.get("ruv")
    if not ruv:
        logger.warning("Message missing RUV: %s", payload)
        return

    with app.app_context():
        card = CreditCardModel.query.filter_by(ruv=ruv).first()
        if not card:
            logger.warning("Card with RUV %s not found", ruv)
            return

        _, data = client.get_card_status(ruv)
        logger.info("TrueNative status for %s: %s", ruv, data)

        mapped_status = map_status(data.get("status") if isinstance(data, dict) else None)
        if not mapped_status:
            logger.info("Status %s not final, skipping", data)
            return

        if card.status == mapped_status:
            logger.debug("Card %s already in status %s", card.id, mapped_status)
        else:
            card.mark_status(mapped_status)
            if isinstance(data, dict) and data.get("issuer"):
                try:
                    card.issuer = CardIssuer.from_external(data.get("issuer"))
                except Exception:
                    logger.debug("Unable to map issuer %s", data.get("issuer"))
            db.session.commit()
            logger.info("Card %s transitioned to %s", card.id, mapped_status.value)

            try:
                context = {
                    "name": payload.get("fullName"),
                    "ruv": card.ruv,
                    "last_four": card.last_four_digits,
                    "issuer": card.issuer.value if card.issuer else "DESCONOCIDO",
                }
                if mapped_status == CardStatus.APROBADA:
                    notifier.send_card_approved(payload.get("email"), context)
                elif mapped_status == CardStatus.RECHAZADA:
                    notifier.send_card_rejected(payload.get("email"), context)
            except Exception as exc:
                logger.warning("Failed to send email for %s: %s", card.id, exc)

        if receipt_handle:
            consumer.delete_message(receipt_handle)


def run() -> None:
    poll_interval = int(os.environ.get("CARDS_POLLER_INTERVAL", "15"))
    app = create_context()
    consumer = CardsQueueConsumer()
    notifier = NotificationService()
    client = TrueNativeCardsClient()

    while True:
        try:
            messages = list(consumer.fetch_messages())
            if not messages:
                time.sleep(poll_interval)
                continue

            for message in messages:
                try:
                    process_message(app, consumer, client, notifier, message)
                except Exception as exc:
                    logger.exception("Error processing message: %s", exc)
        except KeyboardInterrupt:
            logger.info("Poller interrupted")
            break
        except Exception as exc:
            logger.exception("Unexpected error in poller loop: %s", exc)
            time.sleep(poll_interval)


if __name__ == "__main__":
    run()
