from datetime import datetime
from app.extensions import db


class Session(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(12), db.ForeignKey("users.id"), nullable=False, index=True)
    token = db.Column(db.String(512), unique=True, nullable=False, index=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(512), nullable=True)
    status = db.Column(db.String(20), default='ACTIVE', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)

    user = db.relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<Session {self.id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "token": self.token,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
        }
