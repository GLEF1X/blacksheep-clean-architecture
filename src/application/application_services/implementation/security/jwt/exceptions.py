from src.utils.errors_wrapper import ErrorCatalog
from src.utils.exceptions import ProcessError


class SecurityExceptionCatalog(ErrorCatalog):
    default_area = "security"

    USER_NOT_REGISTERED = ProcessError(hint="User not registered")
    INVALID_SCOPE = ProcessError(hint="Malformed scope name")
    MISSING_API_TOKEN = ProcessError(hint="API Token is empty")
    MALFORMED_API_TOKEN = ProcessError(hint="Token format is invalid")
    INCORRECT_PASSWORD = ProcessError(hint="Password incorrect")
    TOKEN_EXPIRED = ProcessError(hint="Token has expired")
    INVALID_AUTHORIZATION_METHOD = ProcessError()
