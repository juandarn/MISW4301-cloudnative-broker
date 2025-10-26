from db import db
import datetime
import uuid

class PostModel(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.String(), primary_key=True, default=lambda: str(uuid.uuid4()))
    routeId = db.Column(db.String(), nullable=False)
    userId = db.Column(db.String(), nullable=False)
    expireAt = db.Column(db.DateTime(timezone=True), nullable=False)
    createdAt = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)

    def to_dict(self):
        """Convert model to dictionary with ISO format dates"""
        return {
            'id': self.id,
            'routeId': self.routeId,
            'userId': self.userId,
            'expireAt': self.expireAt.isoformat() if self.expireAt else None,
            'createdAt': self.createdAt.isoformat() if self.createdAt else None
        }
