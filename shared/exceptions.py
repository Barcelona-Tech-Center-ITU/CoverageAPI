"""Custom exceptions for GIGA Coverage services."""

from typing import Optional


class CoverageException(Exception):
    """Base exception for GIGA Coverage services."""

    def __init__(self, message: str, code: Optional[str] = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class DatabaseConnectionError(CoverageException):
    """Raised when database connection fails."""

    def __init__(self, message: str = "Database connection failed"):
        super().__init__(message, "DB_CONNECTION_ERROR")


class InvalidAPIKeyError(CoverageException):
    """Raised when API key validation fails."""

    def __init__(self, message: str = "Invalid API key"):
        super().__init__(message, "INVALID_API_KEY")


class ValidationError(CoverageException):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: Optional[str] = None):
        self.field = field
        super().__init__(message, "VALIDATION_ERROR")


class ConfigurationError(CoverageException):
    """Raised when configuration is invalid."""

    def __init__(self, message: str):
        super().__init__(message, "CONFIG_ERROR")
