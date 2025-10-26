from flask import Flask, request
import uuid
from datetime import datetime, timedelta
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import ValidationError
from models.user import UsuarioModel
from db import db
import secrets
import hashlib

from schemas import AuthSchema, UserMeSchema, UserSchema, UserUpdateSchema

# Se utiliza para dividir la aplicación en varios segementos
blp = Blueprint("users", __name__, description="Operations on users")

def generar_salt():
    return secrets.token_hex(32)

def hash_password(password, salt):
    entrada_salada = password + salt
    return hashlib.sha256(entrada_salada.encode()).hexdigest()

@blp.errorhandler(422)
def handle_unprocessable_entity(err):
    messages = err.data.get("messages") if hasattr(err, "data") else str(err)
    return {"message": messages}, 400

@blp.route("/users")
class UserList(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    # 1 - Crea un nuevo usuario
    def post(self, user_data):

        username = user_data.get("username")
        email = user_data.get("email")

        if UsuarioModel.query.filter_by(username=username).first():
            abort(412, message="Username already exists")

        if UsuarioModel.query.filter_by(email=email).first():
            abort(412, message="Email already exists")

        user_data["salt"] = generar_salt()
        user_data["password"] = hash_password(user_data["password"], user_data["salt"])

        nuevo_usuario = UsuarioModel(
            **user_data
        )

        db.session.add(nuevo_usuario)
        db.session.commit()

        return nuevo_usuario

@blp.route("/users/<string:user_id>")
class UserPatch(MethodView):
    # 2 - Actualiza de usuarios
    @blp.arguments(UserUpdateSchema)
    @blp.response(200)
    def patch(self, user_data, user_id,):
        usuario = UsuarioModel.query.get(user_id)
        if not usuario:
            abort(404, message="User not found")

        for campo, valor in user_data.items():
            setattr(usuario, campo, valor)

        usuario.updatedAt = datetime.utcnow()

        db.session.commit()
        return {"msg": "el usuario ha sido actualizado"}

@blp.route("/users/auth")
class UserAuth(MethodView):
    # 3 - Generación de Token
    @blp.arguments(AuthSchema)
    @blp.response(200, AuthSchema)
    def post(self, auth_data):
        username = auth_data.get("username")
        password = auth_data.get("password")

        user = UsuarioModel.query.filter_by(username=username).first()

        if not user:
            abort(404, message="User not found or invalid password")
        
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
        
        token = auth_header.split(" ")[1]
        user = UsuarioModel.query.filter_by(token=token).first()
        if not user:
            abort(401, message="User not found")

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