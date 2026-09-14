from datetime import datetime
from decimal import Decimal
import enum
from app.extensions import db
from app.utils.date_format import format_iso_datetime


class TransactionType(enum.Enum):
    INCOME = "INCOME"
    SPEND = "SPEND"
    REQUEST = "REQUEST"


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.String(16), primary_key=True)
    account_id = db.Column(db.String(16), db.ForeignKey("accounts.id"), nullable=False, index=True)
    type = db.Column(db.Enum(TransactionType), nullable=False)
    amount = db.Column(db.Numeric(precision=15, scale=2), nullable=False)
    idempotency_key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    related_user_id = db.Column(db.String(12), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    account = db.relationship("Account", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction {self.id} {self.type.value} {self.amount}>"

    def to_dict(self):
        return {
            "id": self.id,
            "account_id": self.account_id,
            "type": self.type.value,
            "amount": str(self.amount),
            "idempotency_key": self.idempotency_key,
            "related_user_id": self.related_user_id,
            "description": self.description,
            "created_at": format_iso_datetime(self.created_at),
        }
