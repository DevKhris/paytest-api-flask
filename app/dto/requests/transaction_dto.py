from decimal import Decimal, InvalidOperation
from marshmallow import Schema, fields, validate, validates, ValidationError


class TransferRequest(Schema):
    toUserId = fields.String(
        required=True,
        validate=validate.Length(min=12, max=12),
    )
    amount = fields.Decimal(
        required=True,
        places=2,
    )
    idempotency_key = fields.String(
        required=True,
        validate=validate.Length(min=16, max=64),
    )
    description = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=255),
    )

    @validates("amount")
    def validate_amount(self, value):
        try:
            amount = Decimal(str(value))
            if amount <= 0:
                raise ValidationError("Amount must be greater than zero")
            if amount.is_nan() or amount.is_infinite():
                raise ValidationError("Amount cannot be NaN or infinite")
        except (InvalidOperation, ValueError):
            raise ValidationError("Invalid numeric value for amount")
