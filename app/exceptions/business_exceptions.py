class BusinessError(Exception):
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.status_code = status_code


class AuthenticationError(BusinessError):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, 401)


class UserAlreadyExistsError(BusinessError):
    def __init__(self, message: str = "User already exists"):
        super().__init__(message, 409)


class InvalidCredentialsError(BusinessError):
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message, 401)


class RoomCodeInvalidError(BusinessError):
    def __init__(self, message: str = "Invalid room code"):
        super().__init__(message, 400)


class AccountNotFoundError(BusinessError):
    def __init__(self, message: str = "Account not found"):
        super().__init__(message, 404)


class InsufficientBalanceError(BusinessError):
    def __init__(self, message: str = "Insufficient balance"):
        super().__init__(message, 400)


class InvalidAmountError(BusinessError):
    def __init__(self, message: str = "Invalid amount"):
        super().__init__(message, 400)


class RecipientNotFoundError(BusinessError):
    def __init__(self, message: str = "Recipient not found"):
        super().__init__(message, 404)


class TransactionNotFoundError(BusinessError):
    def __init__(self, message: str = "Transaction not found"):
        super().__init__(message, 404)


class DuplicateTransactionError(BusinessError):
    def __init__(self, message: str = "Duplicate transaction"):
        super().__init__(message, 409)


class ContactNotFoundError(BusinessError):
    def __init__(self, message: str = "Contact not found"):
        super().__init__(message, 404)


class ContactAlreadyExistsError(BusinessError):
    def __init__(self, message: str = "Contact already exists"):
        super().__init__(message, 409)


class CannotAddSelfAsContactError(BusinessError):
    def __init__(self, message: str = "Cannot add yourself as a contact"):
        super().__init__(message, 400)
