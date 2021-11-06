import logging
import os
import sys
from typing import Union, no_type_check

import gunicorn.glogging
from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


class StubbedGunicornLogger(gunicorn.glogging.Logger):
    @no_type_check
    def setup(self, cfg):
        handler = logging.NullHandler()
        self.error_logger = logging.getLogger("gunicorn.error")
        self.error_logger.addHandler(handler)
        self.access_logger = logging.getLogger("gunicorn.access")
        self.access_logger.addHandler(handler)
        self.error_logger.setLevel("DEBUG")
        self.access_logger.setLevel("DEBUG")

    def access(self, resp, req, environ, request_time) -> None:
        status = resp.status
        if isinstance(status, str):
            status = status.split(None, 1)[0]

        self.access_logger.info(
            "request",
            method=environ["REQUEST_METHOD"],
            request_uri=environ["RAW_URI"],
            status=status,
            response_length=getattr(resp, "sent", None),
            request_time_seconds="%d.%06d"
            % (request_time.seconds, request_time.microseconds),
            pid="<%s>" % os.getpid(),
        )


def configure_gunicorn_logger_adapter(
    logging_level: Union[int, str], serialize_records: bool = False
) -> None:
    intercept_handler = InterceptHandler()
    logging.root.setLevel(logging_level)

    seen = set()
    for name in [
        *logging.root.manager.loggerDict.keys(),
        "gunicorn",
        "gunicorn.access",
        "gunicorn.error",
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
    ]:
        if name not in seen:
            seen.add(name.split(".")[0])
            logging.getLogger(name).handlers = [intercept_handler]

    logger.configure(handlers=[{"sink": sys.stdout, "serialize": serialize_records}])
