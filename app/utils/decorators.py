import logging
from functools import wraps
from flask import request, jsonify, g
from marshmallow import ValidationError
from app.services.auth_service import AuthService
from app.exceptions.business_exceptions import BusinessError

logger = logging.getLogger(__name__)
auth_service = AuthService()


def handle_exceptions(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            logger.warning(f"Validation error: {e.messages}")
            return jsonify({"error": str(e.messages)}), 400
        except BusinessError as e:
            logger.warning(f"Business error: {e}")
            return jsonify({"error": str(e)}), e.status_code
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return jsonify({"error": "Internal server error"}), 500
    return decorated_function


def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid authorization header"}), 401

        token = auth_header.replace("Bearer ", "")

        user = auth_service.verify_token(token)
        if not user:
            return jsonify({"error": "Invalid or expired token"}), 401

        g.current_user = user
        g.current_token = token

        return f(*args, **kwargs)

    return decorated_function
