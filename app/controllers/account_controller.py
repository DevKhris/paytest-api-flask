from flask import Blueprint, request, jsonify, g
from marshmallow import ValidationError

from app.services.account_service import AccountService
from app.utils.decorators import handle_exceptions, require_auth

account_bp = Blueprint("accounts", __name__)
account_service = AccountService()


@account_bp.route("/balance", methods=["GET"])
@require_auth
@handle_exceptions
def get_balance():
    user = g.current_user
    balance_data = account_service.get_balance(user)
    return jsonify(balance_data), 200
