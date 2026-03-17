class DomainError(Exception):
    """Base class for all buisness logic errors."""
    pass

class DuplicateResourceError(DomainError):
    """Thrown when attempting to create an existing resource (e.g. a user)."""
    pass

class ResourceNotFoundError(DomainError):
    """Thrown when a foreign key is violated or data is missing."""
    pass