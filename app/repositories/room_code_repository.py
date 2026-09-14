from datetime import datetime
from typing import Optional
from app.extensions import db
from app.models.room_code import RoomCode


class RoomCodeRepository:
    def find_by_code(self, code: str) -> Optional[RoomCode]:
        return RoomCode.query.filter_by(code=code).first()

    def is_valid(self, code: str) -> bool:
        room_code = self.find_by_code(code)
        return room_code is not None

    def mark_as_used(self, code: str) -> bool:
        room_code = self.find_by_code(code)
        if not room_code:
            return False
        room_code.is_used = True
        room_code.used_at = datetime.utcnow()
        db.session.commit()
        return True
