class ApiException(Exception):
    pass


class RateLimitError(ApiException):
    pass


class AuthenticationError(ApiException):
    pass


class QuotaError(ApiException):
    pass


class InvalidInputError(ApiException):
    pass
