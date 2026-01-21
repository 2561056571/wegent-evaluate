"""
Runtime configuration storage for dynamic settings.

This module provides in-memory storage for configuration values that can be
changed at runtime without persisting to database. These values are reset
when the server restarts.
"""

from app.core.config import settings


# Runtime configuration storage (in-memory, not persisted to database)
# This allows dynamic configuration changes that take effect immediately
_runtime_config = {
    "external_api_base_url": None,  # None means use settings.EXTERNAL_API_BASE_URL
    "external_api_username": None,  # None means use settings.EXTERNAL_API_USERNAME
    "external_api_password": None,  # None means use settings.EXTERNAL_API_PASSWORD
}


def get_external_api_base_url() -> str:
    """
    Get the current EXTERNAL_API_BASE_URL.
    Returns the runtime-configured value if set, otherwise falls back to settings.
    """
    if _runtime_config["external_api_base_url"] is not None:
        return _runtime_config["external_api_base_url"]
    return settings.EXTERNAL_API_BASE_URL


def set_external_api_base_url(url: str) -> None:
    """
    Set the EXTERNAL_API_BASE_URL at runtime.
    
    Args:
        url: The new URL to use. Should be a valid URL starting with http:// or https://
    """
    _runtime_config["external_api_base_url"] = url


def reset_external_api_base_url() -> None:
    """
    Reset the EXTERNAL_API_BASE_URL to use the default from settings.
    """
    _runtime_config["external_api_base_url"] = None


def get_external_api_username() -> str:
    """
    Get the current EXTERNAL_API_USERNAME.
    Returns the runtime-configured value if set, otherwise falls back to settings.
    """
    if _runtime_config["external_api_username"] is not None:
        return _runtime_config["external_api_username"]
    return settings.EXTERNAL_API_USERNAME


def set_external_api_username(username: str) -> None:
    """
    Set the EXTERNAL_API_USERNAME at runtime.
    
    Args:
        username: The new username to use.
    """
    _runtime_config["external_api_username"] = username


def get_external_api_password() -> str:
    """
    Get the current EXTERNAL_API_PASSWORD (password).
    Returns the runtime-configured value if set, otherwise falls back to settings.
    """
    if _runtime_config["external_api_password"] is not None:
        return _runtime_config["external_api_password"]
    return settings.EXTERNAL_API_PASSWORD


def set_external_api_password(password: str) -> None:
    """
    Set the EXTERNAL_API_PASSWORD (password) at runtime.
    
    Args:
        password: The new password to use.
    """
    _runtime_config["external_api_password"] = password
