class DomainError(Exception):
    """Base class for user-visible domain failures."""


class PermissionDenied(DomainError):
    pass


class NotFound(DomainError):
    pass


class ConflictError(DomainError):
    pass
