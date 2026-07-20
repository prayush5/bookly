from fastapi import status

class BooklyException(Exception):
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class InvalidToken(BooklyException):
    def __init__(self):
        super().__init__(
            message="Invalid or expired token", 
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class RevokedToken(BooklyException):
    def __init__(self):
        super().__init__(
            message="Token has been revoked", 
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class AccessTokenRequired(BooklyException):
    def __init__(self):
        super().__init__(
            message="Access token required", 
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class RefreshTokenRequired(BooklyException):
    def __init__(self):
        super().__init__(
            message="Refresh token required", 
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class UserAlreadyExists(BooklyException):
    def __init__(self):
        super().__init__(
            message="User already exists", 
            status_code=status.HTTP_409_CONFLICT
        )

class InsufficientPermission(BooklyException):
    def __init__(self):
        super().__init__(
            message="Insufficient permission", 
            status_code=status.HTTP_403_FORBIDDEN
        )

class BookNotFound(BooklyException):
    def __init__(self):
        super().__init__(
            message="Book not found", 
            status_code=status.HTTP_404_NOT_FOUND
        )

class UserNotFound(BooklyException):
    def __init__(self):
        super().__init__(
            message="User not found", 
            status_code=status.HTTP_404_NOT_FOUND
        )

class InvalidCredentials(BooklyException):
    def __init__(self):
        super().__init__(
            message="Invalid username or password", 
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class NoFieldsToUpdate(BooklyException):
    def __init__(self):
        super().__init__(
            message="Atleast one field must be provided", 
            status_code=status.HTTP_400_BAD_REQUEST
        )

class ReviewExists(BooklyException):
    def __init__(self):
        super().__init__(
            message="Review for this book already exists", 
            status_code=status.HTTP_400_BAD_REQUEST
        )

class NoFieldsToUpdate(BooklyException):
    def __init__(self):
        super().__init__(
            message="No fields to update", 
            status_code=status.HTTP_404_NOT_FOUND
        )

class ReviewNotFound(BooklyException):
    def __init__(self):
        super().__init__(
            message="Review for this book not found", 
            status_code=status.HTTP_404_NOT_FOUND
        )