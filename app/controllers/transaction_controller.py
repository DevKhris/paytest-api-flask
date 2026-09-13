from decimal import Decimal
from flask import Blueprint, request, jsonify, g
from marshmallow import ValidationError

from app.services.transaction_service import TransactionService
from app.models.transaction import TransactionType
from app.dto.requests.transaction_dto import TransferRequest
from app.utils.decorators import handle_exceptions, require_auth

transaction_bp = Blueprint("transactions", __name__)
transaction_service = TransactionService()

transfer_schema = TransferRequest()


@transaction_bp.route("", methods=["GET"])
@require_auth
@handle_exceptions
def get_transactions():
    user = g.current_user

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    transaction_type = request.args.get("type", None, type=str)

    if transaction_type:
        try:
            transaction_type = TransactionType(transaction_type)
        except ValueError:
            return jsonify({"error": "Invalid transaction type"}), 400

    transactions_data = transaction_service.get_transactions(
        user=user,
        page=page,
        per_page=per_page,
        transaction_type=transaction_type,
    )
    return jsonify(transactions_data), 200


@transaction_bp.route("/transfer", methods=["POST"])
@require_auth
@handle_exceptions
def transfer():
    user = g.current_user
    data = transfer_schema.load(request.json)

    result = transaction_service.transfer(
        sender=user,
        toUserId=data["toUserId"],
        amount=Decimal(str(data["amount"])),
        idempotency_key=data["idempotency_key"],
        description=data.get("description"),
    )
    return jsonify(result), 200
