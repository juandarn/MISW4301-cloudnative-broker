from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint
from datetime import datetime, timezone
import uuid
import requests

from config import load_config


blp = Blueprint("rf004", __name__, description="RF-004: Crear oferta y registrar score")


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


def fetch_simple(name, url, payload=None, timeout=5, method="auto", token=None):
    """Cliente HTTP básico.
    name: etiqueta lógica (user, post, routes, offers, scores)
    url: endpoint base (puede incluir / al final)
    payload: dict para POST
    method: 'auto'|'get'|'post'
    token: token sin prefijo Bearer
    Retorna {name: data|{"code":int,"msg":str}}
    """
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        req_url = url
        # Ajustar concatenación de id sólo si el endpoint espera <id>
        if payload and "id" in payload and name in ["post", "routes"]:
            if not req_url.endswith("/"):
                req_url += "/"
            req_url = f"{req_url}{payload['id']}"

        is_get = method == "get" or (
            method == "auto"
            and name in ["user", "routes", "post"]
            and "id" in (payload or {})
        )
        if is_get:
            res = requests.get(req_url, headers=headers, timeout=timeout)
        else:
            res = requests.post(req_url, json=payload, headers=headers, timeout=timeout)

        # Manejo explícito de códigos
        if res.status_code == 401:
            return {name: {"code": 401, "msg": "Token no válido o expirado"}}
        if res.status_code == 403:
            return {name: {"code": 403, "msg": "No autorizado"}}
        if res.status_code == 404:
            return {name: {"code": 404, "msg": "Recurso no encontrado"}}
        if res.status_code == 412:
            return {name: {"code": 412, "msg": "Precondición fallida"}}
        if res.status_code >= 400:
            try:
                j = res.json()
                return {
                    name: {
                        "code": res.status_code,
                        "msg": j.get("msg") or j.get("message") or "Error del servicio",
                    }
                }
            except Exception:
                return {name: {"code": res.status_code, "msg": "Error del servicio"}}

        # Éxito
        data_json = None
        try:
            data_json = res.json()
        except Exception:
            data_json = res.text
        return {name: data_json}
    except Exception as e:
        print(f"[DEBUG] Error fetch_simple {name}: {e}")
        return {name: {"code": 503, "msg": str(e)}}


def ping_critical_services():
    """
    Hace ping a los servicios críticos para RF-004 (user, post, offers)
    usando los ping_url definidos en el dev.yaml y respetando el timeout.
    Devuelve (True, None) si todos responden, o (False, nombre_servicio) si falla alguno.
    """
    CONFIG = load_config("dev")
    critical_services = ["user", "post", "offers"]

    for name in critical_services:
        conf = CONFIG["services"][name]
        ping_url = conf.get("ping_url")
        timeout = conf.get("timeout", 5)

        try:
            res = requests.get(ping_url, timeout=timeout)
            res.raise_for_status()
        except requests.RequestException:
            return False, name  # Indica qué servicio falló

    return True, None


@blp.route("/rf004/posts/<string:post_id>/offers")
class RF004CreateOffer(MethodView):
    @blp.response(201)
    def post(self, post_id):
        try:
            print(f"[DEBUG RF004] Iniciando RF-004 para post_id: {post_id}")
            ok, service = ping_critical_services()
            if not ok:
                print(f"[DEBUG RF004] Ping failed for service: {service}")
                return {"msg": "El servicio está temporalmente fuera de servicio."}, 503

            token = request.headers.get("Authorization", "").replace("Bearer ", "")
            if not token:
                return {"code": 403, "msg": "Token requerido"}, 403

            body = request.get_json(silent=True) or {}
            required_fields = ["description", "size", "fragile", "offer"]
            if any(field not in body for field in required_fields):
                return {
                    "code": 400,
                    "msg": "Cuerpo inválido. Faltan campos requeridos",
                }, 400

            if (
                not isinstance(body.get("offer"), (int, float))
                or body.get("offer") <= 0
            ):
                return {"code": 400, "msg": "El valor de offer debe ser mayor a 0"}, 400
            if body.get("size") not in ["LARGE", "MEDIUM", "SMALL"]:
                return {
                    "code": 400,
                    "msg": "El tamaño debe ser LARGE, MEDIUM o SMALL",
                }, 400

            CONFIG = load_config("dev")

            # Usuario
            user_res = fetch_simple(
                "user",
                CONFIG["services"]["user"]["url"],
                timeout=CONFIG["services"]["user"].get("timeout", 5),
                method="get",
                token=token,
            )
            user_data = user_res.get("user")
            if not user_data or isinstance(user_data, dict) and "code" in user_data:
                code = user_data.get("code") if isinstance(user_data, dict) else 503
                if code in (401, 403):
                    return user_data, code
                return {
                    "code": 503,
                    "msg": "El servicio está temporalmente fuera de servicio.",
                }, 503
            user_id = user_data.get("id")

            # Publicación
            post_res = fetch_simple(
                "post",
                CONFIG["services"]["post"]["url"],
                {"id": post_id},
                timeout=CONFIG["services"]["post"].get("timeout", 5),
                method="get",
                token=token,
            )
            post_data = post_res.get("post")
            if not post_data or isinstance(post_data, dict) and "code" in post_data:
                if isinstance(post_data, dict) and post_data.get("code") == 404:
                    return {"code": 404, "msg": "La publicación no existe."}, 404
                return {
                    "code": 503,
                    "msg": "El servicio está temporalmente fuera de servicio.",
                }, 503

            # Dueño
            if str(post_data.get("userId")) == str(user_id):
                return {"code": 412, "msg": "La publicación es del mismo usuario."}, 412

            # Expiración
            expire_at = post_data.get("expireAt") or post_data.get("expiresAt")
            try:
                expire_dt = parse_iso(expire_at)
            except Exception:
                return {"code": 412, "msg": "La publicación ya está expirada."}, 412
            if expire_dt <= datetime.now(timezone.utc):
                return {"code": 412, "msg": "La publicación ya está expirada."}, 412

            bag_value = post_data.get("bagValue")
            if bag_value is None:
                route_id = post_data.get("routeId")
                if route_id:
                    route_res = fetch_simple(
                        "routes",
                        CONFIG["services"]["routes"]["url"],
                        {"id": route_id},
                        timeout=CONFIG["services"]["routes"].get("timeout", 5),
                        method="get",
                        token=token,
                    )
                    route_data = route_res.get("routes")
                    if isinstance(route_data, dict) and "code" in route_data:
                        return {
                            "code": 503,
                            "msg": "El servicio está temporalmente fuera de servicio.",
                        }, 503
                    if route_data:
                        bag_value = route_data.get("bagCost")
            if bag_value is None:
                return {
                    "code": 503,
                    "msg": "El servicio está temporalmente fuera de servicio.",
                }, 503

            occupancy = {"LARGE": 1.0, "MEDIUM": 0.5, "SMALL": 0.25}.get(
                body["size"], 1.0
            )
            score_value = float(body["offer"]) - (occupancy * float(bag_value))

            offers_base = CONFIG["services"]["offers"]["url"]
            # Asegurar base POST /offers
            if "?" in offers_base:
                offers_base = offers_base.split("?")[0]
            if not offers_base.endswith("/offers"):
                if offers_base.endswith("/offers/"):
                    offers_base = offers_base[:-1]
                elif offers_base.endswith("/offers"):
                    pass
                else:
                    # Derivar de ping_url
                    ping_url = CONFIG["services"]["offers"].get("ping_url", "")
                    if ping_url.endswith("/ping"):
                        offers_base = ping_url[:-5]

            create_offer_payload = {
                "postId": post_id,
                "userId": user_id,
                "description": body["description"],
                "size": body["size"],
                "fragile": body["fragile"],
                "offer": body["offer"],
            }
            offer_res = fetch_simple(
                "offers",
                offers_base,
                create_offer_payload,
                timeout=CONFIG["services"]["offers"].get("timeout", 5),
                method="post",
                token=token,
            )
            offer_data = offer_res.get("offers")
            if not offer_data or isinstance(offer_data, dict) and "code" in offer_data:
                return {
                    "code": 503,
                    "msg": "El servicio está temporalmente fuera de servicio.",
                }, 503
            offer_id = offer_data.get("id")
            if not offer_id:
                return {
                    "code": 503,
                    "msg": "El servicio está temporalmente fuera de servicio.",
                }, 503

            # Score (best effort)
            try:
                scores_url = CONFIG["services"]["scores"]["url"]
                if scores_url:
                    if not scores_url.endswith("/"):
                        scores_url += "/"
                    score_payload = {"oferta_id": offer_id, "utilidad": score_value}
                    fetch_simple(
                        "scores",
                        scores_url,
                        score_payload,
                        timeout=CONFIG["services"]["scores"].get("timeout", 5),
                        method="post",
                        token=token,
                    )
            except Exception as e:
                print("[DEBUG RF004] Error registrando score (ignorado):", e)

            response_data = {
                "data": {
                    "id": offer_id,
                    "userId": offer_data.get("userId") or user_id,
                    "createdAt": offer_data.get("createdAt"),
                    "postId": post_id,
                },
                "msg": f"Oferta creada y utilidad registrada (score={score_value}).",
            }
            return response_data, 201
        except Exception as e:
            print(f"[DEBUG RF004] Excepción no controlada: {e}")
            import traceback

            traceback.print_exc()
            return {
                "code": 503,
                "msg": "El servicio está temporalmente fuera de servicio.",
            }, 503
