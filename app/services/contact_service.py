import logging
from typing import Dict, Any

from app.models.user import User
from app.repositories.contact_repository import ContactRepository
from app.repositories.user_repository import UserRepository
from app.exceptions.business_exceptions import (
    ContactNotFoundError,
    ContactAlreadyExistsError,
    CannotAddSelfAsContactError,
)

logger = logging.getLogger(__name__)


class ContactService:
    def __init__(self):
        self.contact_repo = ContactRepository()
        self.user_repo = UserRepository()

    def add_contact(self, owner: User, contactUserId: str) -> Dict[str, Any]:
        if owner.id == contactUserId:
            raise CannotAddSelfAsContactError("Cannot add yourself as a contact")

        contact_user = self.user_repo.get_by_id(contactUserId)
        if not contact_user:
            raise ContactNotFoundError(f"User with ID {contactUserId} not found")

        if self.contact_repo.exists_contact(owner.id, contact_user.id):
            raise ContactAlreadyExistsError("Contact already exists")

        contact = self.contact_repo.create(
            owner_id=owner.id,
            contact_user_id=contact_user.id,
        )
        logger.info(f"Contact added: {owner.id} -> {contactUserId}")

        return contact.to_dict()

    def get_contacts(self, owner: User) -> Dict[str, Any]:
        contacts, total = self.contact_repo.get_contacts_by_owner_paginated(
            owner_id=owner.id,
            page=1,
            per_page=100,
        )

        return {
            "contacts": [c.to_dict() for c in contacts],
            "total": total,
        }

    def delete_contact(self, owner: User, contactUserId: str) -> bool:
        if not self.contact_repo.exists_contact(owner.id, contactUserId):
            raise ContactNotFoundError("Contact not found")

        self.contact_repo.delete_by_owner_and_contact(owner.id, contactUserId)
        logger.info(f"Contact deleted: {owner.id} -> {contactUserId}")
        return True
