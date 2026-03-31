import json
import logging
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def __init__(
        self,
        *,
        app_name: str,
        app_env: str,
        app_version: str,
    ) -> None:
        super().__init__()
        self.app_name = app_name
        self.app_env = app_env
        self.app_version = app_version

    _default_fields = {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
        "message",
        "asctime",
    }

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "service": self.app_name,
            "environment": self.app_env,
            "version": self.app_version,
            "message": record.getMessage(),
        }

        context = {
            key: value
            for key, value in record.__dict__.items()
            if key not in self._default_fields
        }
        if context:
            payload["context"] = context

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False, default=str)


def setup_logging(
    *,
    app_name: str,
    app_env: str,
    app_version: str,
    log_level: str,
) -> None:
    root_logger = logging.getLogger()
    level = getattr(logging, log_level.upper(), logging.INFO)

    if root_logger.handlers:
        root_logger.setLevel(level)
        return

    handler = logging.StreamHandler()
    handler.setFormatter(
        JsonFormatter(
            app_name=app_name,
            app_env=app_env,
            app_version=app_version,
        )
    )
    root_logger.addHandler(handler)
    root_logger.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
