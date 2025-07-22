"""Logging configuration and utilities."""
import logging
import sys

from ..config import Config


def setup_logging(log_level: str | None = None) -> logging.Logger:
    """
    Configure logging for the application.
    
    Args:
        log_level: Override log level from config
        
    Returns:
        Logger instance for the application
    """
    level = log_level or Config.LOG_LEVEL

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        stream=sys.stderr,
        force=True
    )

    if not Config.DEBUG:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("langchain").setLevel(logging.INFO)
        logging.getLogger("langchain_community").setLevel(logging.INFO)
        logging.getLogger("fastmcp").setLevel(logging.INFO)
        logging.getLogger("uvicorn").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
    else:
        logging.getLogger("fastmcp").setLevel(logging.DEBUG)

    logger = logging.getLogger("cortex_mcp")

    logger.info(f"Logging configured at {level} level")
    if Config.DEBUG:
        logger.debug("Debug mode enabled")

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
