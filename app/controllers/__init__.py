from app.controllers.auth_controller import auth_bp
from app.controllers.account_controller import account_bp
from app.controllers.transaction_controller import transaction_bp
from app.controllers.contact_controller import contact_bp

__all__ = ["auth_bp", "account_bp", "transaction_bp", "contact_bp"]
