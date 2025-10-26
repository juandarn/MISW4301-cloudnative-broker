from __future__ import annotations
import os, re, uuid, time, datetime as dt
from datetime import timezone
from typing import Any, Tuple

from flask import request, jsonify, current_app, Response
from flask.views import MethodView
from flask_smorest import abort, Blueprint

from db import db
from models.credit_card import CreditCardModel, CardStatus, CardIssuer

# Utilitarios (cliente TrueNative + publisher, aunque el publisher puede ser no-op)
from services.cards_queue_publisher import CardsQueuePublisher
from services.truenative_cards_client import TrueNativeCardsClient, TrueNativeException
from services.email_service import GmailEmailClient

blp = Blueprint("credit_cards", __name__)

# ----------------------------- Helpers -----------------------------

def _env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        abort(500, message=f"Missing env var: {name}")
    return v

def _get_bearer_token() -> str:
    auth = request.headers.get("Authorization")
    if not auth:
        abort(403, message="Authorization header is missing")
    parts = auth.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        abort(400, message="Invalid Authorization header")
    return parts[1]

def _resolve_user_or_401() -> dict:
    """Valida el token contra users-app /users/me"""
    import requests
    token = _get_bearer_token()
    try:
        resp = requests.get(
            "http://users-app-service/users/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
    except requests.RequestException as e:
        current_app.logger.warning(f"[users-app] validation failed: {e}")
        abort(401, message="Invalid or expired token")

    if resp.status_code != 200:
        abort(401, message="Invalid or expired token")
    try:
        return resp.json()
    except Exception:
        abort(401, message="Invalid or expired token")

def _normalize_digits(s: str) -> str:
    return re.sub(r"\D", "", s or "")

def _mask_last4(card_number: str) -> str:
    digits = _normalize_digits(card_number)
    if len(digits) < 4:
        abort(400, message="cardNumber invalid (requires at least 4 digits)")
    return digits[-4:]

def _compute_fingerprint(card_number: str, user_id: str) -> str:
    import hashlib
    norm = _normalize_digits(card_number)
    if len(norm) < 8:
        abort(400, message="cardNumber invalid (too short)")
    raw = f"{user_id}:{norm}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def _parse_expiration_or_400(exp: str) -> tuple[int, int]:
    if not re.fullmatch(r"\d{2}/\d{2}", exp or ""):
        abort(400, message="expirationDate must be YY/MM")
    yy, mm = exp.split("/")
    year = 2000 + int(yy)
    month = int(mm)
    if month < 1 or month > 12:
        abort(400, message="expirationDate month invalid")
    return year, month

def _is_expired(year: int, month: int) -> bool:
    now = dt.datetime.utcnow()
    last_day = 28
    for d in (31, 30, 29, 28):
        try:
            dt.datetime(year, month, d)
            last_day = d
            break
        except ValueError:
            continue
    expires_at = dt.datetime(year, month, last_day, 23, 59, 59)
    return now > expires_at

# ----------------- TrueNative & servicios -----------------

def _tn_client() -> TrueNativeCardsClient:
    return TrueNativeCardsClient(
        base_url=os.environ.get("TRUENATIVE_BASE_URL"),
        secret_token=os.environ.get("SECRET_TOKEN"),
        timeout=10,
    )

def _publisher() -> CardsQueuePublisher:
    return CardsQueuePublisher()   # puede ser no-op según tu implementación

# ----------------- Refresh helpers (sin hilos / sin procesos) -----------------

def _persist_status_change(card: CreditCardModel, new_status: CardStatus) -> None:
    card.mark_status(new_status)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[cards] commit failed on refresh: {e}")
        abort(500, message="DB error updating status")

def _should_refresh(card: CreditCardModel) -> bool:
    """Evita refrescar inmediatamente después de crear la tarjeta."""
    try:
        min_age = int(os.environ.get("MIN_REFRESH_AGE_SECONDS", "3"))
    except Exception:
        min_age = 3
    now = dt.datetime.utcnow()
    if not card.created_at:
        return True
    age = (now - card.created_at).total_seconds()
    return age >= min_age

def _refresh_until_final(card: CreditCardModel, max_wait_seconds: int | None = None) -> bool:
    """
    Polling síncrono y acotado. Reintenta cada ~500ms hasta max_wait_seconds.
    Si llega estado final => persiste. Retorna True si cambió.
    """
    if not card or card.status != CardStatus.POR_VERIFICAR:
        return False

    try:
        max_secs = int(max_wait_seconds if max_wait_seconds is not None
                       else os.environ.get("MAX_REFRESH_SECONDS", "12"))
    except Exception:
        max_secs = 12

    client = _tn_client()
    deadline = time.time() + max_secs
    sleep_ms = 0.5  # 500ms
    changed = False

    while time.time() < deadline:
        code, data = client.get_card_status(card.ruv)
        if code == 200:
            status = (data.get("status") or "").upper()
            if status in ("APROBADA", "RECHAZADA"):
                new_status = CardStatus.APROBADA if status == "APROBADA" else CardStatus.RECHAZADA
                _persist_status_change(card, new_status)
                changed = True
            break
        elif code == 202:
            time.sleep(sleep_ms)
            sleep_ms = 0.5 if sleep_ms >= 0.6 else sleep_ms + 0.05
            continue
        elif code in (401, 403, 404):
            current_app.logger.warning(f"[cards] TN refresh stop: HTTP {code}")
            break
        else:
            break

    return changed

# ----------------- Emails -----------------

def _send_pending_email(card: CreditCardModel, user: dict):
    """Correo inicial EN_VERIFICACION"""
    to_email = user.get("email") or user.get("mail")
    if not to_email:
        return
    name = user.get("name") or user.get("fullName")
    issuer_txt = card.issuer.value if card.issuer else "N/D"
    last4 = card.last_four_digits or "****"

    subject = "Estado de tu tarjeta: EN_VERIFICACION"
    text = (
        f"Hola {name or ''},\n\n"
        f"Tu tarjeta {issuer_txt} ****{last4} está en verificación.\n"
        f"RUV: {card.ruv}\n"
        f"Fecha: {dt.datetime.now(timezone.utc).isoformat()}\n"
    )
    html = text.replace("\n", "<br>")

    try:
        GmailEmailClient().send(to_email, subject, html, text)
        current_app.logger.info(f"[email] Enviado correo inicial a {to_email}")
    except Exception as e:
        current_app.logger.warning(f"[email] envío omitido: {e}")

# -------------------------------- Rutas --------------------------------

@blp.route("/credit-cards/ping")
class CreditCardPing(MethodView):
    def get(self):
        return Response("pong", mimetype="text/plain"), 200

@blp.route("/credit-cards/reset")
class CreditCardReset(MethodView):
    def post(self):
        db.drop_all()
        db.create_all()
        return {"msg": "Todos los datos fueron eliminados"}, 200

@blp.route("/credit-cards/count")
class CreditCardCount(MethodView):
    def get(self):
        count = CreditCardModel.query.count()
        return {"count": count}, 200

@blp.route("/credit-cards")
class CreditCardCollection(MethodView):
    def get(self):
        user = _resolve_user_or_401()
        user_id = str(user.get("id") or user.get("userId") or "")

        cards = (CreditCardModel.query
                 .filter_by(user_id=user_id)
                 .order_by(CreditCardModel.created_at.desc())
                 .all())

        any_changed = False
        for c in cards:
            if c.status == CardStatus.POR_VERIFICAR and _should_refresh(c):
                if _refresh_until_final(c):
                    any_changed = True

        if any_changed:
            cards = (CreditCardModel.query
                     .filter_by(user_id=user_id)
                     .order_by(CreditCardModel.created_at.desc())
                     .all())

        result = []
        for c in cards:
            result.append({
                "id": c.id,
                "token": c.token,
                "userId": c.user_id,
                "lastFourDigits": c.last_four_digits,
                "issuer": c.issuer.value if c.issuer else None,
                "status": c.status.value if c.status else None,
                "createdAt": c.created_at.replace(tzinfo=timezone.utc).isoformat() if c.created_at else None,
                "updatedAt": c.updated_at.replace(tzinfo=timezone.utc).isoformat() if c.updated_at else None,
            })
        return jsonify(result), 200

    def post(self):
        user = _resolve_user_or_401()
        user_id = str(user.get("id") or user.get("userId") or "")
        if not user_id:
            abort(401, message="Invalid or expired token")

        body = request.get_json(silent=True) or {}

        required = ["cardNumber", "cvv", "expirationDate", "cardHolderName"]
        missing = [k for k in required if not body.get(k)]
        if missing:
            abort(400, message="Missing or empty fields: " + ", ".join(missing))

        card_number = _normalize_digits(body["cardNumber"])
        if not card_number.isdigit() or len(card_number) < 12:
            abort(400, message="cardNumber invalid")

        cvv = str(body["cvv"]).strip()
        if not cvv.isdigit() or not (3 <= len(cvv) <= 4):
            abort(400, message="cvv invalid")

        year, month = _parse_expiration_or_400(body["expirationDate"])
        if _is_expired(year, month):
            abort(412, message="Card is expired")

        holder = str(body["cardHolderName"]).strip()
        if len(holder) < 3:
            abort(400, message="cardHolderName invalid")

        fingerprint = _compute_fingerprint(card_number, user_id)
        exists = CreditCardModel.query.filter_by(fingerprint=fingerprint).first()
        if exists:
            abort(409, message="Card already registered")

        # Registrar en TN
        client = _tn_client()
        transaction_identifier = str(uuid.uuid4())
        tn_card = {
            "cardNumber": card_number,
            "cvv": cvv,
            "expirationDate": body["expirationDate"],  # YY/MM
            "cardHolderName": holder,
        }

        try:
            data = client.register_card(tn_card, transaction_identifier)
        except TrueNativeException as e:
            if e.status_code in (400, 401, 403):
                abort(e.status_code, message="TrueNative rejected the request")
            if e.status_code == 409:
                abort(409, message="There is already a verification in progress for this card")
            abort(502, message="TrueNative error registering card")

        ruv = data.get("RUV") or data.get("ruv")
        token = data.get("token") or data.get("cardToken") or str(uuid.uuid4())
        issuer_ext = data.get("issuer")
        issuer_enum = CardIssuer.from_external(issuer_ext)

        if not ruv:
            abort(502, message="TrueNative did not return RUV")

        # Guardar como POR_VERIFICAR
        last4 = _mask_last4(card_number)
        now = dt.datetime.utcnow()
        card = CreditCardModel(
            token=token,
            user_id=user_id,
            last_four_digits=last4,
            ruv=ruv,
            issuer=issuer_enum,
            status=CardStatus.POR_VERIFICAR,
            fingerprint=fingerprint,
            created_at=now,
            updated_at=now,
        )
        db.session.add(card)
        db.session.commit()

        # ----------- Nuevo: correo inmediato ------------
        try:
            _send_pending_email(card, user)
        except Exception as e:
            current_app.logger.warning(f"[email] pending skipped: {e}")
        # -----------------------------------------------

        # Publicar evento (opcional/no-op)
        try:
            _publisher().publish({"type": "card_created", "ruv": ruv, "userId": user_id})
        except Exception as e:
            current_app.logger.warning(f"[cards] publish skipped: {e}")

        # **NO** esperamos aquí: el primer GET debe seguir viendo POR_VERIFICAR
        return {
            "id": card.id,
            "userId": card.user_id,
            "createdAt": card.created_at.replace(tzinfo=timezone.utc).isoformat(),
        }, 201

@blp.route("/credit-cards/<string:card_id>")
class CreditCardResource(MethodView):
    def get(self, card_id: str):
        user = _resolve_user_or_401()
        user_id = str(user.get("id") or user.get("userId") or "")
        card = CreditCardModel.query.get(card_id)
        if not card or card.user_id != user_id:
            abort(404, message="Card not found")

        if card.status == CardStatus.POR_VERIFICAR and _should_refresh(card):
            _refresh_until_final(card)

        card = CreditCardModel.query.get(card_id)

        return {
            "id": card.id,
            "token": card.token,
            "userId": card.user_id,
            "lastFourDigits": card.last_four_digits,
            "issuer": card.issuer.value if card.issuer else None,
            "status": card.status.value if card.status else None,
            "createdAt": card.created_at.replace(tzinfo=timezone.utc).isoformat() if card.created_at else None,
            "updatedAt": card.updated_at.replace(tzinfo=timezone.utc).isoformat() if card.updated_at else None,
        }, 200
