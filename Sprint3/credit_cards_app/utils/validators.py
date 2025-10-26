from __future__ import annotations

import calendar
import re
from datetime import datetime, timezone

from flask_smorest import abort

from models.credit_card import CardIssuer

CARD_NUMBER_REGEX = re.compile(r"^\d{13,19}$")
CVV_REGEX = re.compile(r"^\d{3,4}$")
EXPIRATION_REGEX = re.compile(r"^(\d{2})/(\d{2})$")


def validate_card_number(value: str) -> str:
    digits = value.replace(" ", "")
    if not CARD_NUMBER_REGEX.match(digits):
        abort(400, message="Invalid cardNumber")
    return digits


def validate_cvv(value: str) -> str:
    if not CVV_REGEX.match(value):
        abort(400, message="Invalid cvv")
    return value


def validate_expiration(expiration: str) -> datetime:
    match = EXPIRATION_REGEX.match(expiration)
    if not match:
        abort(400, message="Invalid expirationDate format")

    year_part, month_part = match.groups()
    year = 2000 + int(year_part)
    month = int(month_part)
    if month < 1 or month > 12:
        abort(400, message="Invalid expirationDate month")

    last_day = calendar.monthrange(year, month)[1]
    expires_at = datetime(year, month, last_day, 23, 59, 59, tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    if expires_at < now:
        abort(412, message="Card is expired")
    return expires_at


def detect_issuer(card_number: str) -> CardIssuer:
    number = card_number
    if number.startswith("4"):
        return CardIssuer.VISA
    if number[:2] in {"51", "52", "53", "54", "55"} or (
        len(number) == 16 and 2221 <= int(number[:4]) <= 2720
    ):
        return CardIssuer.MASTERCARD
    if number[:2] in {"34", "37"}:
        return CardIssuer.AMERICAN_EXPRESS
    if number.startswith("6011") or number[:3] in {"644", "645", "646", "647", "648", "649"} or (
        number.startswith("65")
    ):
        return CardIssuer.DISCOVER
    if number[:2] in {"36", "38"} or number[:3] in {"300", "301", "302", "303", "304", "305"}:
        return CardIssuer.DINERS_CLUB
    return CardIssuer.UNKNOWN
