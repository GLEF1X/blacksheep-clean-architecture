
COLORED_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "colored_verbose": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s%(asctime)s | %(log_color)s%(levelname)-8s%(red)s%(name)-21s%(reset)s %(blue)s%(message)s",
        },
        "uvicorn_access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": ' %(client_addr)s - "%(request_line)s" %(status_code)s',
        },
    },
    "handlers": {
        "colored_console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "colored_verbose",
        },
        "uvicorn_access_formatter": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "uvicorn_access",
        },
    },
    "loggers": {
        "": {
            "level": "INFO",
            "handlers": ["colored_console"],
        },
        "gunicorn.access": {"handlers": ["colored_console"]},
        "gunicorn.error": {"handlers": ["colored_console"]},
        "uvicorn.access": {"handlers": ["uvicorn_access_formatter"]},
    },
    "root": {"level": "WARNING", "handlers": ["colored_console"]},
}
