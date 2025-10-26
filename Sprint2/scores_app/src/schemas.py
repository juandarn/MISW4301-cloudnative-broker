from marshmallow import Schema, fields

class ScoreSchema(Schema):
    id = fields.Str(dump_only=True)
    oferta_id = fields.Str(required=True)
    utilidad = fields.Float(required=True)

class ScoreResponseSchema(Schema):
    oferta_id = fields.Str(required=True)
    utilidad = fields.Float(allow_none=True)