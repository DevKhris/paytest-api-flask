from flask import Blueprint, request, jsonify, g
from marshmallow import ValidationError

from app.services.auth_service import AuthService
from app.dto.requests.auth_dto import RoomCodeRequest, RegisterRequest, LoginRequest
from app.dto.responses.auth_response_dto import AuthResponse
from app.utils.decorators import handle_exceptions, require_auth

auth_bp = Blueprint("auth", __name__)
auth_service = AuthService()

room_code_schema = RoomCodeRequest()
register_schema = RegisterRequest()
login_schema = LoginRequest()
auth_response_schema = AuthResponse()


def _build_auth_response(message, user, token_data):
    return auth_response_schema.dump({
        "message": message,
        "user": {
            "userId": user.id,
            "name": user.name,
            "created_at": user.created_at.isoformat(),
            "updatedAt": user.updated_at.isoformat(),
        },
        "token": token_data,
    })


@auth_bp.route("/room-code", methods=["POST"])
@handle_exceptions
def validate_room_code():
    data = room_code_schema.load(request.json)
    auth_service.validate_room_code(data["room_code"])
    return jsonify({"message": "Room code valid", "room_code": data["room_code"]}), 200


@auth_bp.route("/register", methods=["POST"])
@handle_exceptions
def register():
    data = register_schema.load(request.json)

    user, token_data = auth_service.register(
        name=data["name"],
        password=data["password"],
        room_code=data["room_code"],
        ip_address=request.remote_addr,
        user_agent=request.headers.get("User-Agent"),
    )

    response = _build_auth_response("User registered successfully", user, token_data)
    return jsonify(response), 201


@auth_bp.route("/login", methods=["POST"])
@handle_exceptions
def login():
    data = login_schema.load(request.json)

    user, token_data = auth_service.login(
        userId=data["userId"],
        password=data["password"],
        ip_address=request.remote_addr,
        user_agent=request.headers.get("User-Agent"),
    )

    response = _build_auth_response("Login successful", user, token_data)
    return jsonify(response), 200


@auth_bp.route("/logout", methods=["POST"])
@require_auth
@handle_exceptions
def logout():
    token = g.current_token
    auth_service.logout(token)
    return jsonify({"message": "Logout successful"}), 200
