import random
import string
import uuid


class IDGenerator:
    def generate_unique_id(self) -> str:
        chars = string.ascii_uppercase + string.digits
        return "".join(random.choices(chars, k=12))

    def generate_initial_balance(self) -> float:
        return round(random.uniform(100.00, 1000.00), 2)

    def generate_idempotency_key(self) -> str:
        return uuid.uuid4().hex
