from marshmallow import Schema, fields, post_dump

# Origin / Destiny para el trayecto
class AirportSchema(Schema):
    airportCode = fields.String(required=True)
    country = fields.String(required=True)

# Trayecto
class RouteSchema(Schema):
    id = fields.String(required=True)
    flightId = fields.String(required=True)
    origin = fields.Nested(AirportSchema, required=True)
    destiny = fields.Nested(AirportSchema, required=True)
    bagCost = fields.Integer(required=True)
    plannedStartDate = fields.DateTime(required=True)
    plannedEndDate = fields.DateTime(required=True)

# Oferta
class OfferSchema(Schema):
    id = fields.String(required=True)
    userId = fields.String(required=True)
    description = fields.String()
    size = fields.String()
    fragile = fields.Boolean()
    offer = fields.Integer()
    score = fields.Integer()  # utilidad
    createdAt = fields.DateTime(required=True)

# Publicación
class PostSchema(Schema):
    id = fields.String(required=True)
    expireAt = fields.DateTime(required=True)
    route = fields.Nested(RouteSchema, required=True)
    createdAt = fields.DateTime(required=True)
    offers = fields.List(fields.Nested(OfferSchema))

    @post_dump
    def wrap_data(self, data, **kwargs):
        return {"data": data}
