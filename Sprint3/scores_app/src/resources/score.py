from flask import Flask, request
import uuid
from datetime import datetime, timedelta
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import ValidationError
from models.score import ScoreModel
from db import db
import secrets
import hashlib

from schemas import ScoreResponseSchema, ScoreSchema

# Se utiliza para dividir la aplicación en varios segementos
blp = Blueprint("scores", __name__, description="Operations on score")


@blp.route("/<string:oferta_id>")
class ScoreScore(MethodView):
    @blp.response(200, ScoreResponseSchema)
    def get(self, oferta_id):
        score = ScoreModel.query.filter_by(oferta_id=oferta_id).first()
        if not score:
            return {"oferta_id": oferta_id, "utilidad": None}
        return score

@blp.route("/")
class Score(MethodView):
    @blp.arguments(ScoreSchema)
    @blp.response(200, ScoreResponseSchema)
    def post(self, score_data):
        nuevo_score = ScoreModel(
            oferta_id=score_data.get("oferta_id"),
            utilidad=score_data.get("utilidad")  
        )

        db.session.add(nuevo_score)
        db.session.commit()

        return nuevo_score

@blp.route("/ping")
class ScorePing(MethodView):
    # 6 - Verificar estado del servicio
    @blp.response(200)
    def get(self):
        return {"message": "Pong"}
    
@blp.route("/reset")
class ScoreReset(MethodView):
    # 7 - Borrar base de datos
    @blp.response(200)
    def post(self):
        db.drop_all()
        db.create_all()
        return {"msg": "Todos los datos fueron eliminados"}