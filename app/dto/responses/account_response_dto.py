from marshmallow import Schema, fields


class AccountResponse(Schema):
    accountId = fields.String()
    userId = fields.String()
    balance = fields.String()
    created_at = fields.DateTime(format="iso")
    updatedAt = fields.DateTime(format="iso")


class BalanceResponse(Schema):
    balance = fields.String()
    currency = fields.String(default="USD")
