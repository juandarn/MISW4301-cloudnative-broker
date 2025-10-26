from marshmallow import Schema, fields, validates, ValidationError
from datetime import datetime, timezone
import uuid

class PostSchema(Schema):
    id = fields.Str(dump_only=True)
    routeId = fields.Str(required=True)
    userId = fields.Str(required=True)
    expireAt = fields.DateTime(format='iso', required=True)
    createdAt = fields.DateTime(format='iso', dump_only=True)

    @validates('routeId')
    def validate_route_id(self, value):
        try:
            uuid.UUID(value)
        except (ValueError, TypeError):
            raise ValidationError(['Missing data for required field.'])

    @validates('userId')
    def validate_user_id(self, value):
        try:
            uuid.UUID(value)
        except (ValueError, TypeError):
            raise ValidationError(['Missing data for required field.'])

    # Remove expireAt validation from schema since it should return 412, not 400

class PostResponseSchema(Schema):
    id = fields.Str(dump_only=True)
    userId = fields.Str(dump_only=True)
    createdAt = fields.DateTime(format='iso', dump_only=True)

class PostListSchema(Schema):
    id = fields.Str(dump_only=True)
    routeId = fields.Str(dump_only=True)
    userId = fields.Str(dump_only=True)
    expireAt = fields.DateTime(format='iso', dump_only=True)
    createdAt = fields.DateTime(format='iso', dump_only=True)

class PostCountSchema(Schema):
    count = fields.Int(dump_only=True)

class PostResetSchema(Schema):
    msg = fields.Str(dump_only=True)

class PostDeleteSchema(Schema):
    msg = fields.Str(dump_only=True)
