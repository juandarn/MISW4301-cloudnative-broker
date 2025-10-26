from enum import Enum
from db import db
import datetime
import uuid

class Size(Enum):
    LARGE = "LARGE"
    MEDIUM = "MEDIUM"
    SMALL = "SMALL"


class OfferModel(db.Model):
    __tablename__ = "offers"

    id = db.Column(db.String(), primary_key=True, default=lambda: str(uuid.uuid4()))
    postId = db.Column(db.String(), nullable=False)
    userId = db.Column(db.String(), nullable=False)
    description = db.Column(db.String(140))
    size = db.Column(db.Enum(Size), nullable=False)
    fragile = db.Column(db.Boolean(), nullable=False, default=False)
    offer = db.Column(db.Integer(), nullable=False)
    createdAt = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    
    @property
    def status_value(self):
        return self.size.value if self.size else None
