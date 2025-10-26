from __future__ import annotations

from marshmallow import Schema, fields
from marshmallow_enum import EnumField

from models.credit_card import CardIssuer, CardStatus


class CreditCardCreateSchema(Schema):
	user_id = fields.String(required=True, data_key="userId")
	email = fields.Email(required=True)
	full_name = fields.String(required=True, data_key="fullName")
	card_number = fields.String(required=True, data_key="cardNumber")
	expiration_date = fields.String(required=True, data_key="expirationDate")
	cvv = fields.String(required=True)
	document_number = fields.String(required=True, data_key="documentNumber")
	document_type = fields.String(required=False, allow_none=True, data_key="documentType")
	device_id = fields.String(required=False, allow_none=True, data_key="deviceId")
	metadata = fields.Dict(required=False)


class CreditCardSchema(Schema):
	id = fields.String(dump_only=True)
	token = fields.String(dump_only=True)
	user_id = fields.String(dump_only=True, data_key="userId")
	last_four_digits = fields.String(dump_only=True, data_key="lastFourDigits")
	ruv = fields.String(dump_only=True)
	issuer = EnumField(CardIssuer, by_value=True, dump_only=True)
	status = EnumField(CardStatus, by_value=True, dump_only=True)
	created_at = fields.DateTime(dump_only=True, data_key="createdAt")
	updated_at = fields.DateTime(dump_only=True, data_key="updatedAt")


class CreditCardListQuerySchema(Schema):
	user_id = fields.String(load_default=None, data_key="userId")
	status = EnumField(CardStatus, by_value=True, load_default=None)


class CreditCardCountSchema(Schema):
	count = fields.Integer(dump_only=True)


class CreditCardStatusSchema(Schema):
	status = EnumField(CardStatus, by_value=True)


class CreditCardMessageSchema(Schema):
	ruv = fields.String(required=True)
	status = EnumField(CardStatus, by_value=True, required=True)
	issuer = EnumField(CardIssuer, by_value=True, required=False, allow_none=True)
	last_four = fields.String(required=False, allow_none=True, data_key="lastFour")
	user_id = fields.String(required=True, data_key="userId")
	email = fields.Email(required=True)
	full_name = fields.String(required=False, allow_none=True, data_key="fullName")


class PingSchema(Schema):
	message = fields.String(dump_only=True)

