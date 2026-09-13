import hashlib
import time
from typing import Optional


class IdempotencyUtil:
    @staticmethod
    def generate_key(
        account_id: str,
        transaction_type: str,
        amount: str,
        recipient_id: Optional[str] = None,
    ) -> str:
        data = f"{account_id}:{transaction_type}:{amount}:{recipient_id or ''}"
        return hashlib.sha256(data.encode()).hexdigest()

    @staticmethod
    def validate_key(key: str) -> bool:
        if not key or len(key) < 16:
            return False
        return True

    @staticmethod
    def create_client_key() -> str:
        return f"client_{int(time.time() * 1000)}"
