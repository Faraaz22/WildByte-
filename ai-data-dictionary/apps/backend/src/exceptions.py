"""Custom exceptions for the application."""


class DataDictionaryException(Exception):
    """Base exception for all application errors."""

    pass


class DatabaseConnectionError(DataDictionaryException):
    """Raised when database connection fails."""

    pass


class SchemaExtractionError(DataDictionaryException):
    """Raised when schema extraction fails."""

    pass


class AIGenerationError(DataDictionaryException):
    """Raised when AI documentation generation fails."""

    pass


class QualityAnalysisError(DataDictionaryException):
    """Raised when quality analysis fails."""

    pass


class LineageExtractionError(DataDictionaryException):
    """Raised when lineage extraction fails."""

    pass


class SQLValidationError(DataDictionaryException):
    """Raised when SQL query validation fails."""

    pass


class AuthenticationError(DataDictionaryException):
    """Raised when authentication fails."""

    pass


class AuthorizationError(DataDictionaryException):
    """Raised when user is not authorized."""

    pass


class ResourceNotFoundError(DataDictionaryException):
    """Raised when requested resource is not found."""

    pass


class ValidationError(DataDictionaryException):
    """Raised when input validation fails."""

    pass
