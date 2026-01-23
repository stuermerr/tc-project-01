"""Shared logging setup for the interview practice app."""

from __future__ import annotations

import logging
import os

_DEFAULT_LOG_LEVEL = "INFO"
_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def _resolve_log_level(level_name: str | None) -> int:
    # Normalize the configured level name to a logging level integer.
    if not level_name:
        return logging.INFO
    normalized = level_name.strip().upper()
    # Use the logging module's built-in mapping of names to levels.
    level_value = logging._nameToLevel.get(normalized, logging.INFO)
    return level_value


def setup_logging(level_name: str | None = None) -> None:
    """Configure standard console logging for the app."""

    # Resolve the desired level from explicit input or LOG_LEVEL env var.
    resolved_level = _resolve_log_level(level_name or os.getenv("LOG_LEVEL"))
    root_logger = logging.getLogger()
    if root_logger.handlers:
        # Reuse existing handlers but ensure they emit at the desired level.
        root_logger.setLevel(resolved_level)
        for handler in root_logger.handlers:
            handler.setLevel(resolved_level)
        return

    # Configure a simple console handler when no handlers exist yet.
    logging.basicConfig(level=resolved_level, format=_LOG_FORMAT)
