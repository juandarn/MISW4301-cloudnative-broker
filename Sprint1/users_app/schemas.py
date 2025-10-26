from marshmallow import Schema, fields
from marshmallow_enum import EnumField

class UserSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    email = fields.Email(required=True)
    dni = fields.Str(required=True)
    fullName = fields.Str(required=True)
    phoneNumber = fields.Str(required=True)
    id = fields.Str(dump_only=True)
    createdAt = fields.DateTime(dump_only=True)

class UserUpdateSchema(Schema):
    fullName = fields.Str(required=True)
    phoneNumber = fields.Str(required=True)
    dni = fields.Str(required=True)
    status = fields.Str(required=True)

class AuthSchema(Schema):
    username = fields.Str(required=True, load_only=True)
    password = fields.Str(required=True, load_only=True)
    id = fields.Str(dump_only=True)
    token = fields.Str(dump_only=True)
    expireAt = fields.DateTime(dump_only=True)

class UserMeSchema(Schema):
    id = fields.Str(dump_only=True)
    username = fields.Str(dump_only=True)
    email = fields.Email(dump_only=True)
    fullName = fields.Str(dump_only=True)
    dni = fields.Str(dump_only=True)
    phoneNumber = fields.Str(dump_only=True)
    status = fields.Function(lambda obj: obj.status_value)