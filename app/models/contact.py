from datetime import datetime
from app.extensions import db

class Contact(db.Model):
    __tablename__ = "contacts"

    id = db.Column(db.String(36), primary_key=True)
    owner_user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    contact_user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    owner = db.relationship(
        "User",
        foreign_keys=[owner_user_id],
        back_populates="contacts",
    )
    contact_user = db.relationship(
        "User",
        foreign_keys=[contact_user_id],
        lazy="joined",
    )

    __table_args__ = (
        db.UniqueConstraint("owner_user_id", "contact_user_id", name="uq_owner_contact"),
    )

    def __repr__(self):
        return f"<Contact {self.id}>"
