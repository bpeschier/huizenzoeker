class FilterDoesNotExistError(Exception):
    """
    Raised when a filter does not exist.
    """
    pass


class APIError(Exception):
    """
    Error returned by the API.
    """
    pass


class ValidationError(Exception):
    """
    Raised when filters receive invalid data
    """
    pass