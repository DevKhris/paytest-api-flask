from marshmallow import Schema, fields


class UserResponse(Schema):
    userId = fields.String()
    name = fields.String()
    created_at = fields.DateTime(format="iso")
    updatedAt = fields.DateTime(format="iso")


class TokenResponse(Schema):
    access_token = fields.String()
    token_type = fields.String(default="Bearer")
    expires_in = fields.Integer()


class AuthResponse(Schema):
    message = fields.String()
    user = fields.Nested(UserResponse)
    token = fields.Nested(TokenResponse)
