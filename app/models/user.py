from datetime import datetime
from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(12), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    account = db.relationship("Account", back_populates="user", uselist=False)
    sessions = db.relationship("Session", back_populates="user")
    contacts = db.relationship(
        "Contact",
        foreign_keys="Contact.owner_id",
        back_populates="owner",
    )

    def __repr__(self):
        return f"<User {self.id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
