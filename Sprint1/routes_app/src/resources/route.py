from flask import Blueprint, request, jsonify, Response
from sqlalchemy import select
from db import SessionLocal
from models.route import Route
from schemas import (
    RouteCreateSchema,
    RouteOutSchema,
    parse_iso_naive,
    utc_now_naive,
    to_iso_utc,
    is_valid_uuid,
)
import uuid as _uuid

bp = Blueprint("routes", __name__)
create_schema = RouteCreateSchema()
out_schema = RouteOutSchema()
outs_schema = RouteOutSchema(many=True)


# /routes/ping
@bp.get("/ping")
def ping_routes():
    return Response("pong", mimetype="text/plain")


# Crear trayecto
@bp.post("")
def create_route():
    data = request.get_json(silent=True) or {}
    # 400 si falta cualquier campo
    errors = create_schema.validate(data)
    if errors:
        return Response(status=400)

    # Validación de fechas -> 412 con mensaje si no pasan
    try:
        ps = parse_iso_naive(data["plannedStartDate"])
        pe = parse_iso_naive(data["plannedEndDate"])
    except Exception:
        return jsonify({"msg": "Las fechas del trayecto no son válidas"}), 412

    now = utc_now_naive()
    if ps < now or pe <= ps:
        return jsonify({"msg": "Las fechas del trayecto no son válidas"}), 412

    db = SessionLocal()
    try:
        # flightId único -> 412 (sin cuerpo)
        exists = db.execute(
            select(Route).where(Route.flight_id == data["flightId"])
        ).scalar_one_or_none()
        if exists:
            return Response(status=412)

        rid = str(_uuid.uuid4())
        created = utc_now_naive()
        r = Route(
            id=rid,
            flight_id=data["flightId"],
            source_airport_code=data["sourceAirportCode"],
            source_country=data["sourceCountry"],
            destiny_airport_code=data["destinyAirportCode"],
            destiny_country=data["destinyCountry"],
            bag_cost=int(data["bagCost"]),
            planned_start_date=ps,
            planned_end_date=pe,
            created_at=created,
            updated_at=created,
        )
        db.add(r)
        db.commit()
        return jsonify({"id": rid, "createdAt": to_iso_utc(created)}), 201
    finally:
        db.close()


# Listar / filtrar
@bp.get("")
def list_routes():
    flight = request.args.get("flight")
    if flight is not None and flight.strip() == "":
        return Response(status=400)
    db = SessionLocal()
    try:
        stmt = select(Route)
        if flight:
            stmt = stmt.where(Route.flight_id == flight)
        rows = db.execute(stmt).scalars().all()
        out = [
            {
                "id": r.id,
                "flightId": r.flight_id,
                "sourceAirportCode": r.source_airport_code,
                "sourceCountry": r.source_country,
                "destinyAirportCode": r.destiny_airport_code,
                "destinyCountry": r.destiny_country,
                "bagCost": r.bag_cost,
                "plannedStartDate": to_iso_utc(r.planned_start_date),
                "plannedEndDate": to_iso_utc(r.planned_end_date),
                "createdAt": to_iso_utc(r.created_at),
            }
            for r in rows
        ]
        return jsonify(out)
    finally:
        db.close()


# Consultar por id
@bp.get("/<id>")
def get_route(id: str):
    if not is_valid_uuid(id):
        return Response(status=400)
    db = SessionLocal()
    try:
        r = db.get(Route, id)
        if not r:
            return Response(status=404)
        return jsonify(
            {
                "id": r.id,
                "flightId": r.flight_id,
                "sourceAirportCode": r.source_airport_code,
                "sourceCountry": r.source_country,
                "destinyAirportCode": r.destiny_airport_code,
                "destinyCountry": r.destiny_country,
                "bagCost": r.bag_cost,
                "plannedStartDate": to_iso_utc(r.planned_start_date),
                "plannedEndDate": to_iso_utc(r.planned_end_date),
                "createdAt": to_iso_utc(r.created_at),
            }
        )
    finally:
        db.close()


# Eliminar
@bp.delete("/<id>")
def delete_route(id: str):
    if not is_valid_uuid(id):
        return Response(status=400)
    db = SessionLocal()
    try:
        r = db.get(Route, id)
        if not r:
            return Response(status=404)
        db.delete(r)
        db.commit()
        return jsonify({"msg": "el trayecto fue eliminado"})
    finally:
        db.close()


# Contador
@bp.get("/count")
def count_routes():
    db = SessionLocal()
    try:
        c = db.query(Route).count()
        return jsonify({"count": c})
    finally:
        db.close()
