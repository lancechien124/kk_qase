"""
Logging Configuration
"""
import sys
import json
from loguru import logger
from pathlib import Path
from typing import Any, Dict
from datetime import datetime

from app.core.config import settings


def structured_log_formatter(record: Dict[str, Any]) -> str:
    """
    Format log record as structured JSON
    
    Args:
        record: Log record dictionary
    
    Returns:
        JSON formatted log string
    """
    log_data = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["name"],
        "function": record["function"],
        "line": record["line"],
    }
    
    # Add extra fields if present
    if "extra" in record:
        log_data.update(record["extra"])
    
    # Add exception info if present
    if "exception" in record:
        log_data["exception"] = {
            "type": record["exception"].type.__name__ if record["exception"].type else None,
            "value": str(record["exception"].value) if record["exception"].value else None,
            "traceback": record["exception"].traceback if record["exception"].traceback else None,
        }
    
    return json.dumps(log_data, ensure_ascii=False, default=str)


def setup_logging():
    """Setup application logging"""
    # Remove default handler
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True,
    )
    
    # Add file handler
    log_path = Path("logs")
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Standard log file
    logger.add(
        log_path / "app_{time:YYYY-MM-DD}.log",
        rotation="00:00",  # Rotate at midnight
        retention="30 days",  # Keep logs for 30 days
        compression="zip",  # Compress old logs
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.LOG_LEVEL,
        encoding="utf-8",
    )
    
    # Structured JSON log file
    logger.add(
        log_path / "structured_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="30 days",
        compression="zip",
        format=structured_log_formatter,
        level=settings.LOG_LEVEL,
        encoding="utf-8",
        serialize=True,  # Output as JSON
    )
    
    # Error log file (only errors)
    logger.add(
        log_path / "error_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="30 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        encoding="utf-8",
    )
    
    logger.info("Logging configured successfully")
