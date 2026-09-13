from marshmallow import Schema, fields, validate


class AddContactRequest(Schema):
    contactUserId = fields.String(
        required=True,
        validate=validate.Length(min=12, max=12),
    )
