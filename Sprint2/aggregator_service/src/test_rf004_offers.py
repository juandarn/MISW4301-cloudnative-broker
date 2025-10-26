import json
from types import SimpleNamespace

from app import create_app


class DummyResp:
    def __init__(self, status_code, json_data=None):
        self.status_code = status_code
        self._json = json_data or {}
    def json(self):
        return self._json


def build_client(monkeypatch, cases):
    """cases: dict with keys: me, post, route, offer_create, score_create, offer_delete"""
    import resources.rf004_offers as r

    class DummyClients(r.ServiceClients):
        def __init__(self):
            pass
        def get_me(self, token, rid):
            return cases.get("me", DummyResp(200, {"id": "user-1"}))
        def get_post(self, post_id, rid):
            return cases.get("post", DummyResp(200, {"id": post_id, "userId": "owner-1", "expireAt": "2999-01-01T00:00:00Z", "bagValue": 100}))
        def get_route(self, route_id, rid):
            return cases.get("route", DummyResp(200, {"id": route_id, "bagCost": 100}))
        def create_offer(self, payload, rid):
            return cases.get("offer_create", DummyResp(201, {"id": "offer-1", "userId": payload.get("userId"), "createdAt": "2999-01-01T00:00:00Z", "postId": payload.get("postId")}))
        def create_score(self, offer_id, score, rid):
            return cases.get("score_create", DummyResp(200, {"oferta_id": offer_id, "utilidad": score}))
        def delete_offer(self, offer_id, rid):
            return cases.get("offer_delete", DummyResp(200, {}))

    monkeypatch.setattr(r, "ServiceClients", DummyClients)


def make_app_client():
    app = create_app()
    app.testing = True
    return app.test_client()


def _auth_headers():
    return {"Authorization": "Bearer token-1", "Content-Type": "application/json"}


def test_201_happy_path_with_post_bagvalue(monkeypatch):
    build_client(monkeypatch, {"me": DummyResp(200, {"id": "user-2"})})
    client = make_app_client()
    body = {"description": "abc", "size": "LARGE", "fragile": True, "offer": 150}
    resp = client.post("/rf004/posts/post-1/offers", data=json.dumps(body), headers=_auth_headers())
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["data"]["postId"] == "post-1"
    assert "msg" in data and data["msg"]


def test_201_happy_path_with_route_bagvalue(monkeypatch):
    post_json = {"id": "post-1", "userId": "owner-1", "expireAt": "2999-01-01T00:00:00Z", "routeId": "route-9"}
    build_client(monkeypatch, {
        "me": DummyResp(200, {"id": "user-2"}),
        "post": DummyResp(200, post_json),
        "route": DummyResp(200, {"id": "route-9", "bagCost": 80})
    })
    client = make_app_client()
    body = {"description": "abc", "size": "MEDIUM", "fragile": False, "offer": 100}
    resp = client.post("/rf004/posts/post-1/offers", data=json.dumps(body), headers=_auth_headers())
    assert resp.status_code == 201


def test_400_invalid_body(monkeypatch):
    build_client(monkeypatch, {})
    client = make_app_client()
    body = {"description": "", "size": "HUGE", "fragile": True, "offer": -1}
    resp = client.post("/rf004/posts/post-1/offers", data=json.dumps(body), headers=_auth_headers())
    assert resp.status_code == 400


def test_403_missing_auth(monkeypatch):
    build_client(monkeypatch, {})
    client = make_app_client()
    body = {"description": "abc", "size": "SMALL", "fragile": True, "offer": 10}
    resp = client.post("/rf004/posts/post-1/offers", data=json.dumps(body), headers={"Content-Type": "application/json"})
    assert resp.status_code == 403


def test_401_invalid_token(monkeypatch):
    build_client(monkeypatch, {"me": DummyResp(401, {})})
    client = make_app_client()
    body = {"description": "abc", "size": "SMALL", "fragile": True, "offer": 10}
    resp = client.post("/rf004/posts/post-1/offers", data=json.dumps(body), headers=_auth_headers())
    assert resp.status_code == 401


def test_404_post_not_found(monkeypatch):
    build_client(monkeypatch, {"post": DummyResp(404, {})})
    client = make_app_client()
    body = {"description": "abc", "size": "SMALL", "fragile": True, "offer": 10}
    resp = client.post("/rf004/posts/post-1/offers", data=json.dumps(body), headers=_auth_headers())
    assert resp.status_code == 404


def test_412_same_owner(monkeypatch):
    post_json = {"id": "post-1", "userId": "user-2", "expireAt": "2999-01-01T00:00:00Z"}
    build_client(monkeypatch, {"me": DummyResp(200, {"id": "user-2"}), "post": DummyResp(200, post_json)})
    client = make_app_client()
    body = {"description": "abc", "size": "SMALL", "fragile": True, "offer": 10}
    resp = client.post("/rf004/posts/post-1/offers", data=json.dumps(body), headers=_auth_headers())
    assert resp.status_code == 412


def test_412_expired_post(monkeypatch):
    post_json = {"id": "post-1", "userId": "owner-1", "expireAt": "2000-01-01T00:00:00Z"}
    build_client(monkeypatch, {"me": DummyResp(200, {"id": "user-2"}), "post": DummyResp(200, post_json)})
    client = make_app_client()
    body = {"description": "abc", "size": "SMALL", "fragile": True, "offer": 10}
    resp = client.post("/rf004/posts/post-1/offers", data=json.dumps(body), headers=_auth_headers())
    assert resp.status_code == 412


def test_503_fail_bagvalue_via_route(monkeypatch):
    post_json = {"id": "post-1", "userId": "owner-1", "expireAt": "2999-01-01T00:00:00Z", "routeId": "route-9"}
    build_client(monkeypatch, {"me": DummyResp(200, {"id": "user-2"}), "post": DummyResp(200, post_json), "route": DummyResp(500, {})})
    client = make_app_client()
    body = {"description": "abc", "size": "SMALL", "fragile": True, "offer": 10}
    resp = client.post("/rf004/posts/post-1/offers", data=json.dumps(body), headers=_auth_headers())
    assert resp.status_code == 503


def test_503_fail_scores_with_compensation(monkeypatch):
    build_client(monkeypatch, {
        "me": DummyResp(200, {"id": "user-2"}),
        "score_create": DummyResp(500, {})
    })
    client = make_app_client()
    body = {"description": "abc", "size": "SMALL", "fragile": True, "offer": 10}
    resp = client.post("/rf004/posts/post-1/offers", data=json.dumps(body), headers=_auth_headers())
    assert resp.status_code == 503


