from flask import Flask, jsonify, request
from uuid import UUID
from datetime import datetime, timedelta
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import ValidationError
from models.offer import OfferModel, Size

from db import db
from schemas import OfferOutputSchema, PostOfferSchema

# Se utiliza para dividir la aplicación en varios segementos
blp = Blueprint("offers", __name__, description="Operations on offers")


@blp.errorhandler(422)
def handle_unprocessable_entity(err):
    messages = err.data.get("messages") if hasattr(err, "data") else str(err)
    return {"message": messages}, 400

def is_valid_uuid(val):
    try:
        UUID(str(val))
        return True
    except ValueError:
        return False

@blp.route("/offers")
class OfferList(MethodView):
    @blp.arguments(PostOfferSchema)
    @blp.response(201, PostOfferSchema)
    # 1 - Crea una oferta
    def post(self, offer_data):
        size = offer_data.get("size")
        offer = offer_data.get("offer")
        userid = offer_data.get("userId")
        postid = offer_data.get("postId")

        if not is_valid_uuid(userid):
            abort(400, message="Invalid user ID")

        if not is_valid_uuid(postid):
            abort(400, message="Invalid post ID")


        if offer < 0:
            abort(412, message="Invalid offer value")

        if size not in [s.value for s in Size]:
            abort(412, message="Invalid size value")
            
        offer = OfferModel(**offer_data)

        db.session.add(offer)
        db.session.commit()
        return offer

    blp.response(200, OfferOutputSchema(many=True))
    def get(self):
        post_id = request.args.get("post")
        owner_id = request.args.get("owner")

        query = OfferModel.query
        if post_id:
            query = query.filter_by(postId=post_id)
        if owner_id:
            query = query.filter_by(userId=owner_id)

        offers = query.all()

        result = [{
            "id": o.id,
            "postId": o.postId,
            "userId": o.userId,
            "description": o.description,
            "size": o.size.value if o.size else None,
            "fragile": o.fragile,
            "offer": o.offer,
            "createdAt": o.createdAt.isoformat() if o.createdAt else None
        } for o in offers]
        
        return jsonify(result), 200

@blp.route("/offers/<string:offer_id>")
class Offer(MethodView):
    @blp.response(200, PostOfferSchema)
    def get(self, offer_id):
        if not is_valid_uuid(offer_id):
            abort(400, message="Invalid offer ID")
        offer = OfferModel.query.get(offer_id)
        if not offer:
            abort(404, message="Offer not found")
        return offer
    
    @blp.response(200)
    def delete(self, offer_id):
        if not is_valid_uuid(offer_id):
            abort(400, message="Invalid offer ID")
        offer = OfferModel.query.get(offer_id)
        if not offer:
            abort(404, message="Offer not found")

        db.session.delete(offer)
        db.session.commit()
        return {"msg": "la oferta fue eliminada"}
    
@blp.route("/offers/count")
class OfferCount(MethodView):
    @blp.response(200)
    def get(self):
        count = OfferModel.query.count()
        return {"count": count}
    
@blp.route("/offers/ping")
class OfferPing(MethodView):
    @blp.response(200)
    def get(self):
        return {"msg": "pong"}

@blp.route("/offers/reset")
class OfferReset(MethodView):
    @blp.response(200)
    def post(self):
        db.session.query(OfferModel).delete()
        db.session.commit()
        return {"msg": "Todos los datos fueron eliminados"}
