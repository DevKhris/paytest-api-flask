from datetime import datetime
from app.extensions import db

class Session(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    token = db.Column(db.String(512), unique=True, nullable=False, index=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(512), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    user = db.relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<Session {self.id}>"
