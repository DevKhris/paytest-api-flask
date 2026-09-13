from marshmallow import Schema, fields, validate, validates, ValidationError


class RoomCodeRequest(Schema):
    room_code = fields.String(
        required=True,
        validate=validate.Length(min=4, max=10),
    )


class RegisterRequest(Schema):
    name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100),
    )
    password = fields.String(
        required=True,
        validate=validate.Length(min=6, max=128),
        load_only=True,
    )
    room_code = fields.String(
        required=True,
        validate=validate.Length(min=4, max=10),
    )


class LoginRequest(Schema):
    userId = fields.String(
        required=True,
        validate=validate.Length(min=12, max=12),
    )
    password = fields.String(
        required=True,
        load_only=True,
    )
