from marshmallow import Schema, fields, ValidationError
from datetime import datetime, timezone
import uuid

ISO_FMT = "%Y-%m-%dT%H:%M:%S"


def to_iso_utc(dt: datetime) -> str:
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt.strftime(ISO_FMT)


def utc_now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def parse_iso_naive(s: str) -> datetime:
    # Acepta '...Z' o con offset; normaliza a UTC naive
    try:
        if s.endswith("Z"):
            s = s[:-1]
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    except Exception as e:
        raise ValidationError("Invalid ISO datetime") from e


def is_valid_uuid(s: str) -> bool:
    try:
        uuid.UUID(str(s))
        return True
    except Exception:
        return False


class RouteCreateSchema(Schema):
    flightId = fields.String(required=True)
    sourceAirportCode = fields.String(required=True)
    sourceCountry = fields.String(required=True)
    destinyAirportCode = fields.String(required=True)
    destinyCountry = fields.String(required=True)
    bagCost = fields.Integer(required=True)
    # Los dejamos como string para controlar el 412 de fechas inválidas
    plannedStartDate = fields.String(required=True)
    plannedEndDate = fields.String(required=True)


class RouteOutSchema(Schema):
    id = fields.String(required=True)
    flightId = fields.String(required=True)
    sourceAirportCode = fields.String(required=True)
    sourceCountry = fields.String(required=True)
    destinyAirportCode = fields.String(required=True)
    destinyCountry = fields.String(required=True)
    bagCost = fields.Integer(required=True)
    plannedStartDate = fields.String(required=True)
    plannedEndDate = fields.String(required=True)
    createdAt = fields.String(required=True)
