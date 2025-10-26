from __future__ import annotations

import datetime as dt
import enum
import uuid

from db import db


class CardStatus(enum.Enum):
    POR_VERIFICAR = "POR_VERIFICAR"
    RECHAZADA = "RECHAZADA"
    APROBADA = "APROBADA"


class CardIssuer(enum.Enum):
    VISA = "VISA"
    MASTERCARD = "MASTERCARD"
    AMERICAN_EXPRESS = "AMERICAN EXPRESS"
    DISCOVER = "DISCOVER"
    DINERS_CLUB = "DINERS CLUB"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_external(cls, issuer: str | None) -> "CardIssuer":
        if not issuer:
            return cls.UNKNOWN
        normalized = issuer.strip().upper()
        for member in cls:
            if member.value == normalized:
                return member
        return cls.UNKNOWN


class CreditCardModel(db.Model):
    __tablename__ = "credit_cards"

    id = db.Column(db.String(), primary_key=True, default=lambda: str(uuid.uuid4()))
    token = db.Column(db.String(256), nullable=False)
    user_id = db.Column(db.String(), nullable=False, index=True)
    last_four_digits = db.Column(db.String(4), nullable=False)
    ruv = db.Column(db.String(), nullable=False, unique=True)
    issuer = db.Column(db.Enum(CardIssuer), nullable=False, default=CardIssuer.UNKNOWN)
    status = db.Column(db.Enum(CardStatus), nullable=False, default=CardStatus.POR_VERIFICAR)
    created_at = db.Column(db.DateTime(), default=dt.datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(), default=dt.datetime.utcnow, nullable=False)
    fingerprint = db.Column(db.String(128), nullable=False)

    def mark_status(self, status: CardStatus) -> None:
        self.status = status
        self.updated_at = dt.datetime.utcnow()

    @property
    def status_value(self) -> str:
        return self.status.value if self.status else None

    @property
    def issuer_value(self) -> str:
        return self.issuer.value if self.issuer else None
