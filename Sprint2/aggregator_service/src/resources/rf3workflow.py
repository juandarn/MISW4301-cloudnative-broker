import requests
from config import load_config
import json

CONFIG = load_config("rf3workflow")


def check_existing_post(user_id, route_id):
    """Verifica si ya existe un post creado por el usuario para la ruta indicada."""
    if not user_id or not route_id:
        return {"code": 400, "msg": "user_id o route_id faltante"}

    url = f"{CONFIG['services']['post']['url']}?route={route_id}&owner={user_id}"
    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        posts = res.json()

        if not isinstance(posts, list):
            posts = []

        if posts:
            return {
                "code": 412,
                "msg": "El usuario ya tiene una publicación para la misma fecha"
            }

        return {"code": 200, "msg": "No existe post para esta ruta"}
    except requests.exceptions.RequestException as e:
        print("[DEBUG] Error al verificar post existente:", e)
        return {"code": 503, "msg": "No se pudo verificar si existe un post"}


def fetch_simple(name, url, payload=None, timeout=5, method="auto"):
    """
    Llama al microservicio de manera síncrona.
    method: 'auto' (GET para user/routes sin id, POST para todo lo demás), 'get', 'post'
    """
    try:
        headers = {}
        if payload and "token" in payload:
            headers["Authorization"] = f"Bearer {payload['token']}"

        if payload and "id" in payload and name in ["post", "routes", "user"]:
            url = f"{url}{payload['id']}"

        # Determinar método
        if method == "get" or (method == "auto" and name in ["user", "routes"] and "id" not in (payload or {})):
            res = requests.get(url, headers=headers, timeout=timeout)
        else:
            res = requests.post(url, json=payload, headers=headers, timeout=timeout)

        res.raise_for_status()
        return {name: res.json()}

    except Exception as e:
        print(f"[DEBUG] Error fetch_simple {name}:", e)
        return {name: {"code": 503, "msg": str(e)}}


def call_microservices_simple(payloads=None):
    if payloads is None:
        payloads = {}
    results = {}
    route_id = None
    route_data_for_response = None

    # 1️⃣ Usuario
    if 'user' in payloads:
        user_payload = payloads['user']
        user_res = fetch_simple('user', CONFIG['services']['user']['url'], user_payload)
        print("[DEBUG] Respuesta fetch_simple usuario:", user_res)
        user_data = user_res.get('user')
        if not user_data or 'error' in user_data or 'code' in user_data:
            error_msg = user_data.get('msg') if user_data else "Usuario no válido o no encontrado"
            print("[DEBUG] Error en usuario:", error_msg)
            return {"code": 401, "msg": error_msg}
        results['user'] = user_data

    # 2️⃣ Ruta
    if 'route' in payloads:
        route_payload = payloads['route']
        print("[DEBUG] Payload de ruta recibido:", route_payload)

        # Buscar rutas existentes por flightId
        existing_routes_res = fetch_simple(
            'routes',
            f"{CONFIG['services']['routes']['url']}?flight={route_payload.get('flightId')}",
            method="get"
        )
        print("[DEBUG] Respuesta fetch_simple rutas existentes:", existing_routes_res)

        existing_routes = existing_routes_res.get('routes', [])
        if isinstance(existing_routes, dict):
            existing_routes = existing_routes.get('data', [])
        elif isinstance(existing_routes, str):
            existing_routes = json.loads(existing_routes)

        if existing_routes:
            # Si la ruta ya existe, verificamos si hay post
            first_route = existing_routes[0]
            route_id = first_route.get('id')
            route_data_for_response = first_route

            if 'post' in payloads and 'user' in results:
                user_id = results['user']['id']
                check_post_res = check_existing_post(user_id, route_id)
                print("[DEBUG] Resultado de check_existing_post:", check_post_res)
                if check_post_res.get("code") == 412:
                    return check_post_res  # Retorna 412 si ya existe

        else:
            # Crear ruta si no existe
            create_route_res = fetch_simple(
                'routes_create',
                CONFIG['services']['routes']['url'],
                route_payload,
                method="post"
            )
            print("[DEBUG] Respuesta fetch_simple creación de ruta:", create_route_res)
            if 'routes_create' in create_route_res and 'error' not in create_route_res['routes_create']:
                first_created_route = create_route_res['routes_create'][0] if isinstance(create_route_res['routes_create'], list) else create_route_res['routes_create']
                route_id = first_created_route.get('id')
                route_data_for_response = first_created_route
            else:
                return {"code": 503, "msg": "Error al crear la ruta"}

        print("[DEBUG] Ruta seleccionada/creada:", route_data_for_response)

    # 3️⃣ Crear post
    if 'post' in payloads:
        post_payload = payloads['post']
        if 'user' in results:
            post_payload['userId'] = results['user']['id']
        if route_id:
            post_payload['routeId'] = route_id
        print("[DEBUG] Payload de post a crear:", post_payload)

        post_res = fetch_simple('post', CONFIG['services']['post']['url'], post_payload)
        print("[DEBUG] Respuesta fetch_simple post:", post_res)
        if 'post' not in post_res or 'code' in post_res.get('post', {}):
            error_msg = post_res['post'].get('msg', 'Error al crear la publicación') if 'post' in post_res else 'Error al crear la publicación'
            return {"code": 503, "msg": error_msg}
        results['post'] = post_res['post']

    results['route_used'] = route_data_for_response
    print("[DEBUG] Resultado final del workflow:", results)
    return results


def ping_critical_services():
    """
    Hace ping a los servicios críticos para RF005 (user, post, offers)
    usando los ping_url definidos en el dev.yaml y respetando el timeout.
    Devuelve (True, None) si todos responden, o (False, nombre_servicio) si falla alguno.
    """
    critical_services = ["user", "post", "routes"]

    for name in critical_services:
        conf = CONFIG["services"][name]
        ping_url = conf.get("ping_url")
        timeout = conf.get("timeout", 5)

        try:
            res = requests.get(ping_url, timeout=timeout)
            res.raise_for_status()
        except requests.RequestException as e:
            return False, name  # Indica qué servicio falló

    return True, None


def run_workflow_simple(payloads=None):
    return call_microservices_simple(payloads)
