import jwt
import logging
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from flask import current_app

from app.models.user import User
from app.models.transaction import TransactionType
from app.repositories.user_repository import UserRepository
from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.room_code_repository import RoomCodeRepository
from app.utils.hash import HashUtil
from app.utils.id_generator import IDGenerator
from app.exceptions.business_exceptions import (
    AuthenticationError,
    InvalidCredentialsError,
    RoomCodeInvalidError,
)

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.account_repo = AccountRepository()
        self.transaction_repo = TransactionRepository()
        self.session_repo = SessionRepository()
        self.room_code_repo = RoomCodeRepository()
        self.hash_util = HashUtil()
        self.id_generator = IDGenerator()

    def validate_room_code(self, room_code: str) -> bool:
        if not self.room_code_repo.is_valid(room_code):
            logger.warning(f"Invalid room code attempt: {room_code}")
            raise RoomCodeInvalidError("Invalid room code")
        return True

    def register(
        self,
        name: str,
        password: str,
        room_code: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Tuple[User, Dict[str, Any]]:
        self.validate_room_code(room_code)

        unique_id = self.id_generator.generate_unique_id()
        while self.user_repo.exists_by_unique_id(unique_id):
            unique_id = self.id_generator.generate_unique_id()

        password_hash = self.hash_util.hash_password(password)

        user = self.user_repo.create(
            id=unique_id,
            name=name,
            password_hash=password_hash,
        )
        logger.info(f"User registered: {unique_id}")

        account = self.account_repo.create(user_id=user.id)
        logger.info(f"Account created for user: {unique_id}")

        initial_amount = self.id_generator.generate_initial_balance()
        idempotency_key = self.id_generator.generate_idempotency_key()

        transaction = self.transaction_repo.create(
            account_id=account.id,
            type=TransactionType.INCOME,
            amount=initial_amount,
            idempotency_key=idempotency_key,
            description="Saldo inicial de bienvenida",
        )
        logger.info(f"Initial transaction created: {transaction.id}, amount: {initial_amount}")

        token_data = self._generate_token(user, ip_address, user_agent)

        return user, token_data

    def login(
        self,
        userId: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Tuple[User, Dict[str, Any]]:
        user = self.user_repo.get_by_id(userId)
        if not user:
            logger.warning(f"Login attempt for non-existent user: {userId}")
            raise InvalidCredentialsError("Invalid credentials")

        if not self.hash_util.verify_password(password, user.password_hash):
            logger.warning(f"Invalid password for user: {userId}")
            raise InvalidCredentialsError("Invalid credentials")

        token_data = self._generate_token(user, ip_address, user_agent)
        logger.info(f"User logged in: {userId}")

        return user, token_data

    def logout(self, token: str) -> bool:
        session = self.session_repo.get_by_token(token)
        if not session:
            return False

        session.status = 'EXPIRED'
        self.session_repo.save(session)
        logger.info(f"User logged out, session deactivated")
        return True

    def verify_token(self, token: str) -> Optional[User]:
        try:
            payload = jwt.decode(
                token,
                current_app.config["JWT_SECRET_KEY"],
                algorithms=["HS256"],
            )
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None

        session = self.session_repo.get_by_token(token)
        if not session or session.status == 'EXPIRED':
            return None

        if session.expires_at < datetime.utcnow():
            session.status = 'EXPIRED'
            self.session_repo.save(session)
            return None

        user = self.user_repo.get_by_id(payload["user_id"])
        return user

    def _generate_token(
        self,
        user: User,
        ip_address: Optional[str],
        user_agent: Optional[str],
    ) -> Dict[str, Any]:
        expires_delta = current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
        expires_at = datetime.utcnow() + expires_delta

        payload = {
            "user_id": user.id,
            "exp": expires_at,
            "iat": datetime.utcnow(),
        }

        token = jwt.encode(
            payload,
            current_app.config["JWT_SECRET_KEY"],
            algorithm="HS256",
        )

        self.session_repo.create(
            user_id=user.id,
            token=token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
            status='ACTIVE',
        )

        return {
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": int(expires_delta.total_seconds()),
        }
