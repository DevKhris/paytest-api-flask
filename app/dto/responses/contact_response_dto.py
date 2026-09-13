from marshmallow import Schema, fields


class ContactUserInfo(Schema):
    userId = fields.String()
    name = fields.String()


class ContactResponse(Schema):
    id = fields.String()
    ownerId = fields.String()
    contactUserId = fields.String()
    contact = fields.Nested(ContactUserInfo)
    created_at = fields.DateTime(format="iso")


class ContactListResponse(Schema):
    contacts = fields.List(fields.Nested(ContactResponse))
    total = fields.Integer()
