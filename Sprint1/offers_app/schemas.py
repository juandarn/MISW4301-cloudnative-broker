
from marshmallow import Schema, fields, validate
from marshmallow_enum import EnumField
from models.offer import Size

class PostOfferSchema(Schema):
    postId = fields.Str(required=True)
    userId = fields.Str(required=True)
    description = fields.Str(required=True, validate=lambda s: len(s) <= 140)
    size = fields.Str(
        required=True,
    )
    fragile = fields.Bool(required=True)
    offer = fields.Float(required=True)
    
    id = fields.Str(dump_only=True)
    createdAt = fields.DateTime(dump_only=True)

class OfferOutputSchema(Schema):
    id = fields.Str(required=True)
    postId = fields.Str(required=True)
    userId = fields.Str(required=True)
    description = fields.Str(required=True)
    size = fields.Method("get_size")
    fragile = fields.Bool(required=True)
    offer = fields.Float(required=True)
    createdAt = fields.DateTime(required=True)

    def get_size(self, obj):
        return obj.size.value if obj.size else None
    
class GetOfferSchema(Schema):
    id = fields.Str(dump_only=True)
    postId = fields.Str(dump_only=True)
    userId = fields.Str(dump_only=True)
    description = fields.Str(dump_only=True)
    size = fields.Function(lambda obj: obj.size.value if obj.size else None)
    fragile = fields.Bool(dump_only=True)
    offer = fields.Float(dump_only=True)
    createdAt = fields.DateTime(dump_only=True)


