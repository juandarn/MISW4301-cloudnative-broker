from __future__ import annotations

import hashlib
import os
from flask import Request
from flask_smorest import abort


def require_bearer_token(request: Request) -> str:
    """Return the bearer token or abort with proper status code."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        abort(403, message="Authorization header is missing")

    try:
        scheme, token = auth_header.split(" ", 1)
    except ValueError:
        abort(401, message="Invalid Authorization header")

    if scheme.lower() != "bearer" or not token.strip():
        abort(401, message="Invalid Authorization header")

    return token.strip()


def require_env_var(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        abort(500, message=f"Missing env var: {name}")
    return value


def compute_card_fingerprint(card_number: str, pepper: str) -> str:
    """Generate a deterministic fingerprint for a PAN using SHA-256."""
    normalized = card_number.strip().replace(" ", "")
    payload = f"{pepper}:{normalized}"
    return hashlib.sha256(payload.encode()).hexdigest()


def mask_last_four(card_number: str) -> str:
    digits = ''.join(filter(str.isdigit, card_number))
    return digits[-4:] if len(digits) >= 4 else digits.zfill(4)
