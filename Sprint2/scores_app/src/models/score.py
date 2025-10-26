from enum import Enum
from db import db
import datetime
import uuid

class ScoreModel(db.Model):
    __tablename__ = "scores"

    id = db.Column(db.String(), primary_key=True, default=lambda: str(uuid.uuid4()))
    oferta_id = db.Column(db.String(), nullable=False)
    utilidad = db.Column(db.Float(), nullable=False)
    timestamp = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
