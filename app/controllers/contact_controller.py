from flask import Blueprint, request, jsonify, g
from marshmallow import ValidationError

from app.services.contact_service import ContactService
from app.dto.requests.contact_dto import AddContactRequest
from app.utils.decorators import handle_exceptions, require_auth

contact_bp = Blueprint("contacts", __name__)
contact_service = ContactService()

add_contact_schema = AddContactRequest()


@contact_bp.route("", methods=["GET"])
@require_auth
@handle_exceptions
def get_contacts():
    user = g.current_user
    contacts_data = contact_service.get_contacts(user)
    return jsonify(contacts_data), 200


@contact_bp.route("", methods=["POST"])
@require_auth
@handle_exceptions
def add_contact():
    user = g.current_user
    data = add_contact_schema.load(request.json)

    contact_data = contact_service.add_contact(
        owner=user,
        contactUserId=data["contactUserId"],
    )
    return jsonify(contact_data), 201


@contact_bp.route("/<contact_user_id>", methods=["DELETE"])
@require_auth
@handle_exceptions
def delete_contact(contact_user_id):
    user = g.current_user
    contact_service.delete_contact(owner=user, contactUserId=contact_user_id)
    return jsonify({"message": "Contact deleted"}), 200
