from datetime import datetime
from app.extensions import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True)
    unique_id = db.Column(db.String(12), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    account = db.relationship("Account", back_populates="user", uselist=False)
    sessions = db.relationship("Session", back_populates="user")
    contacts = db.relationship(
        "Contact",
        foreign_keys="Contact.owner_user_id",
        back_populates="owner",
    )

    def __repr__(self):
        return f"<User {self.unique_id}>"
