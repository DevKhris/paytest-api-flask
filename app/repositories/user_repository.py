from typing import Optional
from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    def get_by_unique_id(self, unique_id: str) -> Optional[User]:
        return self.find_by(id=unique_id)

    def exists_by_unique_id(self, unique_id: str) -> bool:
        return self.find_by(id=unique_id) is not None
