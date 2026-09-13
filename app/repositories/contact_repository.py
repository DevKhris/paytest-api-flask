from typing import List, Optional
from app.models.contact import Contact
from app.repositories.base_repository import BaseRepository


class ContactRepository(BaseRepository[Contact]):
    def __init__(self):
        super().__init__(Contact)

    def get_by_owner_and_contact(
        self,
        owner_id: str,
        contact_user_id: str,
    ) -> Optional[Contact]:
        return self.find_by(
            owner_id=owner_id,
            contact_user_id=contact_user_id,
        )

    def get_contacts_by_owner(self, owner_id: str) -> List[Contact]:
        return self.find_all_by(owner_id=owner_id)

    def get_contacts_by_owner_paginated(
        self,
        owner_id: str,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[List[Contact], int]:
        query = self.model.query.filter_by(owner_id=owner_id)
        total = query.count()
        contacts = query.offset((page - 1) * per_page).limit(per_page).all()
        return contacts, total

    def exists_contact(self, owner_id: str, contact_user_id: str) -> bool:
        return self.get_by_owner_and_contact(owner_id, contact_user_id) is not None

    def delete_by_owner_and_contact(self, owner_id: str, contact_user_id: str) -> bool:
        contact = self.get_by_owner_and_contact(owner_id, contact_user_id)
        if contact:
            self.delete(contact)
            return True
        return False
