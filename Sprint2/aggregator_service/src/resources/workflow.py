import requests
import logging
from config import load_config
import time
import requests

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG = load_config("dev")

def fetch(name, url, payload=None, timeout=5):
    """
    Llama al microservicio de manera síncrona y devuelve un dict con el nombre del servicio.
    """
    try:
        headers = {}
        if payload and "token" in payload:
            headers["Authorization"] = f"Bearer {payload['token']}"
        
        if payload and "id" in payload and name in ["post", "routes", "user"]:
            url = f"{url}{payload['id']}"
        elif payload and "postId" in payload and name == "offers":
            url = f"{url}{payload['postId']}"
        elif payload and "oferta_id" in payload and name == "scores":
            url = f"{url}{payload['oferta_id']}"

        logger.info(f"DEBUG: Calling {name} service at {url} with headers {headers}")
        res = requests.get(url, headers=headers, timeout=timeout)
        logger.info(f"DEBUG: {name} service response status: {res.status_code}")
        res.raise_for_status()
        result = res.json()
        logger.info(f"DEBUG: {name} service response data: {result}")
        return {name: result}
    except Exception as e:
        logger.error(f"DEBUG: Error calling {name} service: {str(e)}")
        return {name: {"error": str(e)}}


def call_microservices_in_order(payloads=None):
    if payloads is None:
        payloads = {}
    results = {}
    
    # First, get user and post data
    for service_name in ['user', 'post']:
        if service_name in payloads:
            service_conf = CONFIG['services'][service_name]
            url = service_conf['url']
            timeout = service_conf.get('timeout', 5)
            payload = payloads.get(service_name)
            res = fetch(service_name, url, payload, timeout)
            results.update(res)
    
    # Then get other services based on the results
    if 'post' in results and results['post'] and 'error' not in results['post']:
        post_data = results['post']
        post_id = post_data.get('id')
        route_id = post_data.get('routeId')
        
        # Get offers for this post
        if post_id:
            offers_payload = {"postId": post_id}
            if 'user' in results and results['user'] and 'error' not in results['user']:
                offers_payload['token'] = payloads.get('user', {}).get('token')
            offers_res = fetch('offers', CONFIG['services']['offers']['url'], offers_payload, CONFIG['services']['offers'].get('timeout', 5))
            results.update(offers_res)
            
            # Get scores for each offer
            offers = offers_res.get('offers', [])
            if offers and 'error' not in offers:
                for offer in offers:
                    offer_id = offer.get('id')
                    if offer_id:
                        scores_payload = {"oferta_id": offer_id}
                        scores_res = fetch('scores', CONFIG['services']['scores']['url'], scores_payload, CONFIG['services']['scores'].get('timeout', 5))
                        # Add score to the offer
                        if 'scores' in scores_res and 'error' not in scores_res['scores']:
                            offer['score'] = scores_res['scores'].get('utilidad')
        
        # Get route data if routeId exists
        if route_id:
            routes_payload = {"id": route_id}
            routes_res = fetch('routes', CONFIG['services']['routes']['url'], routes_payload, CONFIG['services']['routes'].get('timeout', 5))
            results.update(routes_res)
    
    return results



def ping_critical_services():
    """
    Hace ping a los servicios críticos para RF005 (user, post, offers)
    usando los ping_url definidos en el dev.yaml y respetando el timeout.
    Devuelve (True, None) si todos responden, o (False, nombre_servicio) si falla alguno.
    """
    critical_services = ["user", "post", "offers"]

    for name in critical_services:
        conf = CONFIG["services"][name]
        ping_url = conf.get("ping_url")
        timeout = conf.get("timeout", 5)
        
        try:
            res = requests.get(ping_url, timeout=timeout)
            res.raise_for_status()
            logger.info(f"Ping OK: {name}")
        except requests.RequestException as e:
            logger.error(f"Critical service down: {name} - {str(e)}")
            return False, name  # Indica qué servicio falló

    return True, None




def run_workflow(payloads=None):
    return call_microservices_in_order(payloads)

