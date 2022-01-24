from src.utils.errors_wrapper import ErrorCatalog, ExceptionWithCode


class MediatorExceptionCatalog(ErrorCatalog):
    NOT_FOUND = ExceptionWithCode(hint="Event or command not found")
