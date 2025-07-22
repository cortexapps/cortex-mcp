"""Cortex API client configuration."""

import httpx

from ..config import Config
from ..utils.logging import get_logger

logger = get_logger(__name__)


async def log_request(request: httpx.Request) -> None:
    """Log HTTP request details for debugging."""
    logger.debug(f"Request: {request.method} {request.url}")
    if Config.DEBUG:
        logger.debug(f"Headers: {dict(request.headers)}")


def create_cortex_client() -> httpx.AsyncClient:
    """
    Create and configure the Cortex API client.
    
    Returns:
        Configured httpx.AsyncClient instance
    """
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": Config.USER_AGENT,
    }

    if Config.CORTEX_API_TOKEN:
        headers["Authorization"] = f"Bearer {Config.CORTEX_API_TOKEN}"

    event_hooks = {}
    if Config.DEBUG:
        event_hooks['request'] = [log_request]

    client = httpx.AsyncClient(
        base_url=Config.CORTEX_API_BASE_URL,
        headers=headers,
        event_hooks=event_hooks,
        timeout=httpx.Timeout(30.0),
        follow_redirects=True,
    )

    logger.info(f"Cortex API client configured for: {Config.CORTEX_API_BASE_URL}")
    if Config.CORTEX_API_TOKEN:
        logger.info(f"Using API token: {Config.get_masked_token()}")

    return client
