from flask import request
from datetime import datetime, timezone
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import ValidationError
from models.post import PostModel
from db import db
import uuid
from werkzeug.exceptions import HTTPException

from schemas import (
    PostSchema, 
    PostResponseSchema, 
    PostListSchema, 
    PostCountSchema, 
    PostResetSchema, 
    PostDeleteSchema
)

# Se utiliza para dividir la aplicación en varios segmentos
blp = Blueprint("posts", __name__, description="Operations on posts")

@blp.errorhandler(422)
def handle_unprocessable_entity(err):
    messages = err.data.get("messages") if hasattr(err, "data") else str(err)
    return {"message": {"json": messages}}, 400

@blp.errorhandler(ValidationError)
def handle_validation_error(err):
    return {"message": {"json": err.messages}}, 400

@blp.errorhandler(412)
def handle_precondition_failed(err):
    return {"msg": "La fecha expiración no es válida"}, 412

@blp.route("/posts")
class PostList(MethodView):
    @blp.arguments(PostSchema)
    @blp.response(201, PostResponseSchema)
    def post(self, post_data):
        """1. Creación de publicación"""
        # Validar que la fecha de expiración sea en el futuro
        expire_at = post_data.get("expireAt")
        current_time = datetime.now(timezone.utc)
        
        if expire_at <= current_time:
            abort(412, description="La fecha expiración no es válida")

        nueva_publicacion = PostModel(**post_data)
        db.session.add(nueva_publicacion)
        db.session.commit()

        return nueva_publicacion

    @blp.response(200, PostListSchema(many=True))
    def get(self):
        """2. Ver y filtrar publicaciones"""
        # Obtener parámetros de filtro
        expire = request.args.get("expire")
        route = request.args.get("route")
        owner = request.args.get("owner")

        # Construir query base
        query = PostModel.query

        # Aplicar filtros si están presentes
        if expire is not None and expire != "":
            if expire.lower() not in ['true', 'false']:
                abort(400, message="El parámetro expire debe ser 'true' o 'false'")
            
            expire_bool = expire.lower() == "true"
            current_time = datetime.now(timezone.utc)
            
            if expire_bool:
                # Publicaciones expiradas
                query = query.filter(PostModel.expireAt < current_time)
            else:
                # Publicaciones no expiradas
                query = query.filter(PostModel.expireAt >= current_time)

        if route:
            # Validar que route sea un UUID válido
            try:
                uuid.UUID(route)
            except ValueError:
                abort(400, message="El parámetro route debe ser un UUID válido")
            query = query.filter(PostModel.routeId == route)

        if owner:
            # Validar que owner sea un UUID válido
            try:
                uuid.UUID(owner)
            except ValueError:
                abort(400, message="El parámetro owner debe ser un UUID válido")
            query = query.filter(PostModel.userId == owner)

        posts = query.all()
        return posts

@blp.route("/posts/<string:post_id>")
class Post(MethodView):
    @blp.response(200, PostListSchema)
    def get(self, post_id):
        """3. Consultar una publicación"""
        # Validar formato UUID
        try:
            uuid.UUID(post_id)
        except ValueError:
            abort(400, message="El id no es un valor string con formato uuid")

        post = db.session.get(PostModel, post_id)
        if not post:
            abort(404, message="La publicación con ese id no existe")

        return post

    @blp.response(200, PostDeleteSchema)
    def delete(self, post_id):
        """4. Eliminar publicación"""
        # Validar formato UUID
        try:
            uuid.UUID(post_id)
        except ValueError:
            abort(400, message="El id no es un valor string con formato uuid")

        post = db.session.get(PostModel, post_id)
        if not post:
            abort(404, message="La publicación con ese id no existe")

        db.session.delete(post)
        db.session.commit()

        return {"msg": "la publicación fue eliminada"}

@blp.route("/posts/count")
class PostCount(MethodView):
    @blp.response(200, PostCountSchema)
    def get(self):
        """5. Consultar cantidad de entidades"""
        count = PostModel.query.count()
        return {"count": count}

@blp.route("/posts/ping")
class PostPing(MethodView):
    @blp.response(200)
    def get(self):
        """6. Consulta de salud del servicio"""
        return "pong"

@blp.route("/posts/reset")
class PostReset(MethodView):
    @blp.response(200, PostResetSchema)
    def post(self):
        """7. Restablecer base de datos"""
        PostModel.query.delete()
        db.session.commit()
        return {"msg": "Todos los datos fueron eliminados"}
