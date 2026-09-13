from datetime import datetime
from decimal import Decimal
import enum
from app.extensions import db

class TransactionType(enum.Enum):
    INCOME = "INCOME"
    SPEND = "SPEND"
    REQUEST = "REQUEST"


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.String(36), primary_key=True)
    account_id = db.Column(db.String(36), db.ForeignKey("accounts.id"), nullable=False, index=True)
    type = db.Column(db.Enum(TransactionType), nullable=False)
    amount = db.Column(db.Numeric(precision=12, scale=2), nullable=False)
    idempotency_key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    reference_id = db.Column(db.String(36), db.ForeignKey("transactions.id"), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    account = db.relationship("Account", back_populates="transactions")
    reference = db.relationship("Transaction", remote_side=[id], backref="related_transactions")

    def __repr__(self):
        return f"<Transaction {self.id} {self.type.value} {self.amount}>"
