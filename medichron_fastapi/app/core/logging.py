"""
Structured logging configuration using loguru.
"""
import sys
import json
from pathlib import Path
from loguru import logger

from app.core.config import settings


def json_formatter(record):
    """
    Custom JSON formatter for structured logging.
    """
    log_record = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["module"],
        "function": record["function"],
        "line": record["line"],
    }

    # Add extra fields if present
    if record["extra"]:
        log_record["extra"] = record["extra"]

    # Add exception info if present
    if record["exception"]:
        log_record["exception"] = {
            "type": record["exception"].type.__name__,
            "value": str(record["exception"].value"),
        }

    return json.dumps(log_record)


def setup_logging():
    """
    Configure loguru for the application.
    """
    # Remove default handler
    logger.remove()

    # Add console handler with JSON format for production
    if settings.ENVIRONMENT == "production":
        logger.add(
            sys.stdout,
            format=json_formatter,
            level="INFO",
            serialize=False,  # We use custom json_formatter
            enqueue=True,  # Async-safe
        )
    else:
        # Human-readable format for development
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="DEBUG",
            colorize=True,
            enqueue=True,
        )

    # Add file handler with rotation
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logger.add(
        "logs/app.log",
        format=json_formatter,
        level="INFO",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        enqueue=True,
    )

    # Add error-specific log file
    logger.add(
        "logs/errors.log",
        format=json_formatter,
        level="ERROR",
        rotation="10 MB",
        retention="90 days",
        compression="zip",
        enqueue=True,
    )

    logger.info(f"Logging configured for environment: {settings.ENVIRONMENT}")

    return logger
