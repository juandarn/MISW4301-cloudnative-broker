from flask import Flask, request, current_app
import uuid
from datetime import datetime, timedelta
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import ValidationError
from models.user import UsuarioModel, EstadoUsuario
from db import db
import secrets
import hashlib
import os
import requests
from urllib.parse import urljoin

from services.email_service import GmailEmailClient
from utils.email_templates import tpl_verified, tpl_not_verified

from schemas import AuthSchema, UserMeSchema, UserSchema, UserUpdateSchema

# Se utiliza para dividir la aplicación en varios segmentos
blp = Blueprint("users", __name__, description="Operations on users")

# ----------------- Helpers -----------------

def generar_salt():
    return secrets.token_hex(32)

def hash_password(password, salt):
    entrada_salada = password + salt
    return hashlib.sha256(entrada_salada.encode()).hexdigest()

def _req_env(name: str) -> str:
    val = os.environ.get(name)
    if not val:
        abort(500, message=f"Missing env var: {name}")
    return val

def _verify_signature(verify_token: str, ruv: str, score_raw: str) -> bool:
    """
    Firma del webhook: sha256(SECRET_TOKEN:RUV:SCORE)
    SCORE debe usarse exactamente como llega (string), puede traer decimales.
    """
    secret = _req_env("SECRET_TOKEN")
    token = f"{secret}:{ruv}:{score_raw}"
    calc = hashlib.sha256(token.encode()).hexdigest()
    return calc == verify_token


def _post_truenative_verify(user: UsuarioModel):
    """
    Dispara verificación a TrueNative.
    Envía webhook ABSOLUTO construido con USERS_PUBLIC_BASE_URL (recomendado).
    Si no está definida, usa http://users-app-service como valor por defecto.
    """
    base = _req_env("TRUENATIVE_BASE_URL").rstrip("/")
    secret = _req_env("SECRET_TOKEN")

    # Base para construir URL absoluta del webhook (Service DNS o URL pública)
    public_base = os.environ.get("USERS_PUBLIC_BASE_URL", "http://users-app-service").strip()
    public_base = public_base.rstrip("/") + "/"
    user_webhook = urljoin(public_base, f"users/{user.id}")  # p.ej. http://users-app-service/users/<id>

    url = f"{base}/native/verify"
    headers = {
        "Authorization": f"Bearer {secret}",
        "Content-Type": "application/json",
    }
    payload = {
        "user": {
            "email": user.email,
            "dni": user.dni,
            "fullName": user.fullName,
            "phone": user.phoneNumber,
        },
        "transactionIdentifier": str(uuid.uuid4()),
        "userIdentifier": str(user.id),
        "userWebhook": user_webhook,  # absoluto
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        if resp.status_code != 201:
            current_app.logger.warning(
                f"[TrueNative] verify error ({resp.status_code}): {resp.text}"
            )
        return resp.status_code
    except requests.RequestException as e:
        current_app.logger.error(f"[TrueNative] request failed: {e}")
        return None


# ----------------- Error handler -----------------

@blp.errorhandler(422)
def handle_unprocessable_entity(err):
    messages = err.data.get("messages") if hasattr(err, "data") else str(err)
    return {"message": messages}, 400

# ----------------- Rutas -----------------

@blp.route("/users")
class UserList(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    # 1 - Crea un nuevo usuario (queda POR_VERIFICAR y dispara verificación)
    def post(self, user_data):
        username = user_data.get("username")
        email = user_data.get("email")

        if UsuarioModel.query.filter_by(username=username).first():
            abort(412, message="Username already exists")

        if UsuarioModel.query.filter_by(email=email).first():
            abort(412, message="Email already exists")

        user_data["salt"] = generar_salt()
        user_data["password"] = hash_password(user_data["password"], user_data["salt"])
        # Estado inicial forzado: POR_VERIFICAR
        user_data["status"] = EstadoUsuario.POR_VERIFICAR

        nuevo_usuario = UsuarioModel(**user_data)
        db.session.add(nuevo_usuario)
        db.session.commit()

        # Disparar la verificación (request) a TrueNative
        try:
            _post_truenative_verify(nuevo_usuario)
        except Exception as e:
            current_app.logger.warning(f"Could not enqueue verification for {nuevo_usuario.id}: {e}")

        return nuevo_usuario

@blp.route("/users/<string:user_id>")
class UserPatch(MethodView):

    @blp.response(200)
    def patch(self, user_id):
        usuario = UsuarioModel.query.get(user_id)
        if not usuario:
            abort(404, message="User not found")

        data = request.get_json(silent=True) or {}

        # --- Callback de TrueNative ---
        if all(k in data for k in ("RUV", "score", "verifyToken")):
            ruv = data["RUV"]
            score_raw = str(data["score"])               # usar el string exacto para la firma
            verify_token = data["verifyToken"]

            if not _verify_signature(verify_token, ruv, score_raw):
                abort(401, message="Invalid verifyToken")

            try:
                score_val = float(data["score"])
            except Exception:
                abort(400, message="Invalid score type")

            computed_status = (
                EstadoUsuario.VERIFICADO.value if score_val >= 60.0 else EstadoUsuario.NO_VERIFICADO.value
            )
            usuario.status = EstadoUsuario(computed_status)
            usuario.updatedAt = datetime.utcnow()
            db.session.commit()

            # ------ Enviar correo según resultado (NO romper el webhook si falla) ------
            try:
                mailer = GmailEmailClient()
                nombre = getattr(usuario, "fullName", None)

                if computed_status == EstadoUsuario.VERIFICADO.value:
                    subject = "Tu cuenta fue verificada"
                    html, text = tpl_verified(nombre, score=score_val, threshold=60.0)
                else:
                    subject = "No pudimos verificar tu identidad"
                    html, text = tpl_not_verified(nombre, score=score_val, threshold=60.0)

                mailer.send(usuario.email, subject, html, text)
            except Exception as e:
                # Loguea pero no rompas el webhook
                print(f"[EMAIL ERROR] No se pudo enviar correo a {usuario.email}: {e}")

            # ⬇️ El return va aquí, al nivel del try de arriba (no dentro del except)
            return {"msg": f"Webhook processed. User status set to {computed_status}"}

        # --- Update normal ---
        for campo, valor in data.items():
            setattr(usuario, campo, valor)

        usuario.updatedAt = datetime.utcnow()
        db.session.commit()
        return {"msg": "el usuario ha sido actualizado"}


@blp.route("/users/<string:user_id>/verify")
class UserVerify(MethodView):
    # Reintenta o dispara verificación manualmente (por si falló al crear)
    @blp.response(201)
    def post(self, user_id):
        usuario = UsuarioModel.query.get(user_id)
        if not usuario:
            abort(404, message="User not found")

        if usuario.status == EstadoUsuario.VERIFICADO:
            abort(409, message="User already verified")

        try:
            code = _post_truenative_verify(usuario)
        except Exception as e:
            abort(502, message=f"TrueNative verify request failed: {e}")

        return {"msg": "Verification request sent", "status_code": code}

@blp.route("/users/auth")
class UserAuth(MethodView):
    # 3 - Generación de Token (solo si VERIFICADO)
    @blp.arguments(AuthSchema)
    @blp.response(200, AuthSchema)
    def post(self, auth_data):
        username = auth_data.get("username")
        password = auth_data.get("password")

        user = UsuarioModel.query.filter_by(username=username).first()

        if not user:
            abort(404, message="User not found or invalid password")

        # Bloquear emisión si no está VERIFICADO
        if user.status != EstadoUsuario.VERIFICADO:
            abort(401, message="User is not verified")

        password_hash = hash_password(password, user.salt)
        if password_hash != user.password:
            abort(404, message="User not found or invalid password")

        user.token = str(uuid.uuid4())
        user.expireAt = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()
        return user

@blp.route("/users/me")
class UserMe(MethodView):
    # 4 - Consultar información del usuario
    @blp.response(200, UserMeSchema)
    def get(self):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            abort(403, message="Authorization header is missing")

        try:
            token = auth_header.split(" ")[1]
        except Exception:
            abort(400, message="Invalid Authorization header")

        user = UsuarioModel.query.filter_by(token=token).first()
        if not user:
            abort(401, message="User not found")

        # (opcional) validar expiración del token
        if user.expireAt and user.expireAt < datetime.utcnow():
            abort(401, message="Token expired")

        return user

@blp.route("/users/count")
class UserCount(MethodView):
    # 5 - Contar usuarios
    @blp.response(200)
    def get(self):
        count = UsuarioModel.query.count()
        return {"count": count}

@blp.route("/users/ping")
class UserPing(MethodView):
    # 6 - Verificar estado del servicio
    @blp.response(200)
    def get(self):
        return {"message": "Pong"}

@blp.route("/users/reset")
class UserReset(MethodView):
    # 7 - Borrar base de datos
    @blp.response(200)
    def post(self):
        db.drop_all()
        db.create_all()
        return {"msg": "Todos los datos fueron eliminados"}
