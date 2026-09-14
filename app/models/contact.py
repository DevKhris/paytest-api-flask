from datetime import datetime
from app.extensions import db
from app.utils.date_format import format_iso_datetime


class Contact(db.Model):
    __tablename__ = "contacts"

    id = db.Column(db.String(36), primary_key=True)
    owner_id = db.Column(db.String(12), db.ForeignKey("users.id"), nullable=False, index=True)
    contact_user_id = db.Column(db.String(12), db.ForeignKey("users.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    owner = db.relationship(
        "User",
        foreign_keys=[owner_id],
        back_populates="contacts",
    )
    contact_user = db.relationship(
        "User",
        foreign_keys=[contact_user_id],
        lazy="joined",
    )

    __table_args__ = (
        db.UniqueConstraint("owner_id", "contact_user_id", name="unique_contact"),
    )

    def __repr__(self):
        return f"<Contact {self.id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "contact_user_id": self.contact_user_id,
            "contact": {
                "id": self.contact_user.id,
                "name": self.contact_user.name,
            } if self.contact_user else None,
            "created_at": format_iso_datetime(self.created_at),
        }
