"""Configuration management for Cortex MCP server."""
import os


class Config:
    """Centralized configuration for the application."""

    # API Configuration
    CORTEX_API_TOKEN: str = os.getenv("CORTEX_API_TOKEN", "")
    CORTEX_API_BASE_URL: str = os.getenv("CORTEX_API_BASE_URL", "https://api.getcortexapp.com")

    # Server Configuration
    HOST: str = os.getenv("MCP_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("MCP_PORT", "8000"))
    TRANSPORT: str = os.getenv("MCP_TRANSPORT", "streamable-http")

    # OpenAPI Configuration
    OPENAPI_SPEC_PATH: str = os.getenv(
        "OPENAPI_SPEC_PATH",
        "./swagger.json"
    )

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Application Info
    APP_NAME: str = "Cortex MCP Server"
    USER_AGENT: str = os.getenv("MCP_USER_AGENT", "Cortex-MCP-Server/1.0")

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration values."""
        errors = []

        if not os.path.exists(cls.OPENAPI_SPEC_PATH):
            errors.append(f"OpenAPI spec file not found at: {cls.OPENAPI_SPEC_PATH}")

        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(errors))

    @classmethod
    def get_masked_token(cls) -> str:
        """Return a masked version of the API token for logging."""
        if not cls.CORTEX_API_TOKEN:
            return "NOT_SET"

        if len(cls.CORTEX_API_TOKEN) <= 8:
            return "***"

        return f"{cls.CORTEX_API_TOKEN[:4]}...{cls.CORTEX_API_TOKEN[-4:]}"
