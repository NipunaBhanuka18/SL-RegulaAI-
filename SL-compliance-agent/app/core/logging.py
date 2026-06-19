import sys
from loguru import logger
from app.core.config import get_settings


def setup_logging() -> None:
    """Configure Loguru for structured, readable logs."""
    settings = get_settings()
    logger.remove()  # Remove default handler
    logger.add(
        sys.stdout,
        level=settings.log_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{line}</cyan> — "
            "<level>{message}</level>"
        ),
        colorize=True,
    )
    logger.add(
        "logs/compliance_agent.log",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )
    logger.info("Logging initialised at level: {}", settings.log_level)
