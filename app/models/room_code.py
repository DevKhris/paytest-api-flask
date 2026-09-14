from app.extensions import db


class RoomCode(db.Model):
    __tablename__ = "room_codes"

    code = db.Column(db.String(20), primary_key=True)
    is_used = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<RoomCode {self.code} used={self.is_used}>"
