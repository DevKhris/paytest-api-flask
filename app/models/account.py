from datetime import datetime
from decimal import Decimal
from app.extensions import db

class Account(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="account")
    transactions = db.relationship("Transaction", back_populates="account")

    @property
    def balance(self):
        from app.models.transaction import TransactionType
        from sqlalchemy import func
        
        income = db.session.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).filter(
            Transaction.account_id == self.id,
            Transaction.type == TransactionType.INCOME.value
        ).scalar()
        
        spend = db.session.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).filter(
            Transaction.account_id == self.id,
            Transaction.type == TransactionType.SPEND.value
        ).scalar()
        
        return Decimal(str(income)) - Decimal(str(spend))

    def __repr__(self):
        return f"<Account {self.id}>"
