from datetime import datetime
from typing import Optional, List
from app.models.session import Session
from app.repositories.base_repository import BaseRepository


class SessionRepository(BaseRepository[Session]):
    def __init__(self):
        super().__init__(Session)

    def get_by_token(self, token: str) -> Optional[Session]:
        return self.find_by(token=token)

    def get_active_by_user_id(self, user_id: str) -> List[Session]:
        return self.model.query.filter_by(
            user_id=user_id,
            status='ACTIVE',
        ).all()

    def deactivate_by_token(self, token: str) -> bool:
        session = self.get_by_token(token)
        if session:
            session.status = 'EXPIRED'
            self.save(session)
            return True
        return False

    def deactivate_all_for_user(self, user_id: str) -> int:
        sessions = self.get_active_by_user_id(user_id)
        count = 0
        for session in sessions:
            session.status = 'EXPIRED'
            self.save(session)
            count += 1
        return count

    def cleanup_expired(self) -> int:
        expired = self.model.query.filter(
            self.model.status == 'ACTIVE',
            self.model.expires_at < datetime.utcnow(),
        ).all()
        count = 0
        for session in expired:
            session.status = 'EXPIRED'
            self.save(session)
            count += 1
        return count
