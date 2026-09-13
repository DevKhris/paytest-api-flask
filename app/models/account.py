from datetime import datetime
from decimal import Decimal
from sqlalchemy import func
from app.extensions import db


class Account(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.String(16), primary_key=True)
    user_id = db.Column(db.String(12), db.ForeignKey("users.id"), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="account")
    transactions = db.relationship("Transaction", back_populates="account")

    @property
    def balance(self):
        from app.models.transaction import Transaction, TransactionType

        income = db.session.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).filter(
            Transaction.account_id == self.id,
            Transaction.type == TransactionType.INCOME
        ).scalar()

        spend = db.session.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).filter(
            Transaction.account_id == self.id,
            Transaction.type == TransactionType.SPEND
        ).scalar()

        request = db.session.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).filter(
            Transaction.account_id == self.id,
            Transaction.type == TransactionType.REQUEST
        ).scalar()

        return Decimal(str(income)) - Decimal(str(spend)) - Decimal(str(request))

    def __repr__(self):
        return f"<Account {self.id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "balance": str(self.balance),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
