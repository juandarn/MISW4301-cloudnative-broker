from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from users_app.services.email_service import GmailEmailClient

from credit_cards_app.utils.email_templates import tpl_card_approved, tpl_card_rejected


class NotificationService:
    def __init__(self, email_client: GmailEmailClient | None = None):
        self.email_client = email_client or GmailEmailClient()

    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    def send_card_approved(self, to_email: str, context: dict[str, Any]) -> None:
        timestamp = context.get("timestamp") or self._now()
        html, text = tpl_card_approved(
            context.get("name"),
            context["ruv"],
            context["last_four"],
            context["issuer"],
            timestamp,
        )
        self.email_client.send(
            to_email=to_email,
            subject="Tu tarjeta fue aprobada",
            html_body=html,
            text_body=text,
        )

    def send_card_rejected(self, to_email: str, context: dict[str, Any]) -> None:
        timestamp = context.get("timestamp") or self._now()
        html, text = tpl_card_rejected(
            context.get("name"),
            context["ruv"],
            context["last_four"],
            context["issuer"],
            timestamp,
        )
        self.email_client.send(
            to_email=to_email,
            subject="Tarjeta rechazada",
            html_body=html,
            text_body=text,
        )
