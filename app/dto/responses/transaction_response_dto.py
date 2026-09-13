from marshmallow import Schema, fields


class TransactionResponse(Schema):
    id = fields.String()
    accountId = fields.String()
    type = fields.String()
    amount = fields.String()
    idempotency_key = fields.String()
    relatedUserId = fields.String(allow_none=True)
    description = fields.String(allow_none=True)
    created_at = fields.DateTime(format="iso")


class TransactionListResponse(Schema):
    transactions = fields.List(fields.Nested(TransactionResponse))
    total = fields.Integer()
    page = fields.Integer()
    per_page = fields.Integer()
