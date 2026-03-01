from __future__ import annotations

import logging
from logging.config import dictConfig
from pathlib import Path

from pythonjsonlogger import jsonlogger

from app.config import settings


class JsonFormatter(jsonlogger.JsonFormatter):
    """JSON formatter with stable field names for downstream log processing."""



def setup_logging() -> None:
    """Configure application logging to stdout and file in JSON format."""
    log_path = Path(settings.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": "app.logging_config.JsonFormatter",
                    "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                },
                "file": {
                    "class": "logging.FileHandler",
                    "filename": str(log_path),
                    "formatter": "json",
                },
            },
            "root": {
                "handlers": ["console", "file"],
                "level": "INFO",
            },
        }
    )

    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
