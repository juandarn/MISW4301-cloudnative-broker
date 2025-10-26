from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from datetime import datetime, timezone
from . import workflow  # workflow original para rf005
from . import rf3workflow  # workflow específico para rf003

blp = Blueprint("aggregator", __name__, description="Operations on aggregator")

def to_iso(dt):
    if not dt:
        return None
    if isinstance(dt, str):
        try:
            dt_obj = datetime.fromisoformat(dt.replace("Z", "+00:00"))
            return dt_obj.isoformat()
        except Exception:
            return dt
    elif isinstance(dt, datetime):
        return dt.isoformat()
    return str(dt)

def parse_iso(dt_str):
    """Convierte string ISO a datetime aware en UTC"""
    dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt

@blp.route("/rf003/posts")
class PublicacionCrearView(MethodView):
    @blp.response(201)
    def post(self):

        ok, service = rf3workflow.ping_critical_services()
        if not ok:
            return {"msg": "El servicio está temporalmente fuera de servicio."}, 503

        """Crear publicación y manejar errores del workflow"""
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return {"code": 403, "msg": "Token requerido"}, 403

        body = request.get_json()
        required_fields = ["flightId", "expireAt", "plannedStartDate", "plannedEndDate", "origin", "destiny", "bagCost"]
        if not body or any(field not in body for field in required_fields):
            return {"code": 400, "msg": "Cuerpo inválido. Faltan campos requeridos"}, 400

        # Validación de fechas
        now = datetime.now(timezone.utc)
        fecha_inicio = parse_iso(body["plannedStartDate"])
        fecha_fin = parse_iso(body["plannedEndDate"])
        fecha_expiracion = parse_iso(body["expireAt"])

        if fecha_inicio <= now or fecha_fin <= fecha_inicio:
            return {"code": 412, "msg": "Las fechas del trayecto no son válidas"}, 412
        if fecha_expiracion <= now or fecha_expiracion > fecha_inicio:
            return {"code": 412, "msg": "La fecha expiración no es válida"}, 412

        # Payload de ruta
        route_payload = {
            "flightId": body["flightId"],
            "sourceAirportCode": body["origin"]["airportCode"],
            "sourceCountry": body["origin"]["country"],
            "destinyAirportCode": body["destiny"]["airportCode"],
            "destinyCountry": body["destiny"]["country"],
            "bagCost": body["bagCost"],
            "plannedStartDate": body["plannedStartDate"],
            "plannedEndDate": body["plannedEndDate"]
        }

        # Llamada al workflow
        all_results = rf3workflow.run_workflow_simple({
            "user": {"token": token},
            "route": route_payload,
            "post": {"expireAt": body["expireAt"]}
        })

        # Si el workflow devolvió un error (412, 401, 503, etc)
        if "code" in all_results and "msg" in all_results:
            return all_results, all_results["code"]

        # Todo salió bien, devolver el post creado
        post = all_results["post"]
        route = all_results["route_used"]
        user = all_results["user"]

        response_data = {
            "data": {
                "id": post.get("id"),
                "userId": user.get("id"),
                "createdAt": to_iso(post.get("createdAt")),
                "expireAt": to_iso(body.get("expireAt")),
                "route": {
                    "id": route.get("id"),
                    "createdAt": to_iso(route.get("createdAt"))
                }
            },
            "msg": "Publicación creada exitosamente"
        }

        return response_data, 201


    
@blp.route("/rf005/posts/<string:post_id>")
class PublicacionView(MethodView):

    def head(self, post_id):
        return "", 200
    
    @blp.response(200)
    def get(self, post_id):
        ok, service = workflow.ping_critical_services()
        if not ok:
            return {"msg": "El servicio está temporalmente fuera de servicio."}, 503

        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return {"code": 403, "msg": "Token de autorización requerido"}, 403

        all_results = workflow.run_workflow({
            "user": {"token": token},
            "post": {"id": post_id}
        })

        user = all_results.get("user")
        if not user or "error" in user:
            return {"code": 401, "msg": "Usuario no encontrado"}, 401
        usuario_actual_id = user.get("id")

        post = all_results.get("post")
        if not post or "error" in post:
            return {"code": 404, "msg": "Publicación no encontrada"}, 404

        if str(post.get("userId")) != str(usuario_actual_id):
            return {"code": 403, "msg": "No autorizado"}, 403

        route_data = all_results.get("routes", {})
        route = {
            "id": route_data.get("id"),
            "flightId": route_data.get("flightId"),
            "origin": {
                "airportCode": route_data.get("origin", {}).get("airportCode"),
                "country": route_data.get("origin", {}).get("country")
            },
            "destiny": {
                "airportCode": route_data.get("destiny", {}).get("airportCode"),
                "country": route_data.get("destiny", {}).get("country")
            },
            "bagCost": route_data.get("bagCost")
        } if route_data and "error" not in route_data else None

        offers = all_results.get("offers", [])
        if isinstance(offers, dict) and "error" in offers:
            offers = []

        offers_sorted = sorted(
            [
                {
                    "id": o.get("id"),
                    "userId": o.get("userId"),
                    "description": o.get("description"),
                    "size": o.get("size"),
                    "fragile": o.get("fragile", False),
                    "offer": o.get("offer"),
                    "score": o.get("score"),
                    "createdAt": to_iso(o.get("createdAt"))
                } for o in offers
            ],
            key=lambda x: x.get("score") or 0,
            reverse=True
        )

        response_data = {
            "data": {
                "id": post.get("id"),
                "expireAt": to_iso(post.get("expireAt")),
                "route": route,
                "plannedStartDate": to_iso(route_data.get("plannedStartDate")),
                "plannedEndDate": to_iso(route_data.get("plannedEndDate")),
                "createdAt": to_iso(post.get("createdAt")),
                "offers": offers_sorted
            },
            "msg": "Publicación obtenida exitosamente"
        }

        return response_data, 200


@blp.route("/rf005/ping")
class AggregatorPing(MethodView):
    @blp.response(200)
    def get(self):
        return {"message": "pong", "service": "aggregator"}
