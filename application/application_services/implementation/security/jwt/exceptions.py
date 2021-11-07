class SecurityException(Exception):
    def __init__(self, message: str):
        self.message = message


class UserNotRegistered(SecurityException):
    pass


class APITokenOmittedException(SecurityException):
    pass


class MalformedAPIToken(SecurityException):
    pass


class JWTSubNotExists(SecurityException):
    pass


class IncorrectPassword(SecurityException):
    pass
