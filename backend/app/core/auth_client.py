"""
Authentication client for external API using JWT login.
"""
import time
from typing import Optional

import httpx
import structlog

from app.core.config import settings
from app.core.runtime_config import (
    get_external_api_base_url,
    get_external_api_username,
    get_external_api_password,
)

logger = structlog.get_logger(__name__)


class AuthClient:
    """Authentication client for external API using JWT login."""

    def __init__(self):
        self._token: Optional[str] = None
        self._token_expires_at: float = 0
        self._last_base_url: Optional[str] = None
        self._last_username: Optional[str] = None
        self._last_password: Optional[str] = None

    async def get_access_token(self) -> str:
        """Get a valid access token, refreshing if necessary."""
        current_base_url = get_external_api_base_url()
        current_username = get_external_api_username()
        current_password = get_external_api_password()
        
        # If any credential changed, invalidate the token
        credentials_changed = (
            (self._last_base_url is not None and self._last_base_url != current_base_url) or
            (self._last_username is not None and self._last_username != current_username) or
            (self._last_password is not None and self._last_password != current_password)
        )
        
        if credentials_changed:
            self._token = None
            self._token_expires_at = 0
        
        if self._is_token_valid():
            return self._token

        await self._fetch_new_token()
        return self._token

    def _is_token_valid(self) -> bool:
        """Check if current token is still valid."""
        if not self._token:
            return False
        # Add 60 seconds buffer before expiration
        return time.time() < (self._token_expires_at - 60)

    async def _fetch_new_token(self) -> None:
        """Fetch a new access token by logging in with username and password."""
        base_url = get_external_api_base_url()
        username = get_external_api_username()
        password = get_external_api_password()
        login_url = f"{base_url}{settings.EXTERNAL_API_LOGIN_PATH}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # Use JSON format for login
                response = await client.post(
                    login_url,
                    json={
                        "user_name": username,
                        "password": password,
                    },
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()
                token_data = response.json()

                self._token = token_data.get("access_token")
                if not self._token:
                    raise ValueError("No access_token in response")

                # JWT tokens typically expire in 30 minutes to 24 hours
                # Default to 1 hour if not specified
                expires_in = token_data.get("expires_in", 3600)
                self._token_expires_at = time.time() + expires_in
                
                # Remember the credentials used for this token
                self._last_base_url = base_url
                self._last_username = username
                self._last_password = password

                logger.info(
                    "Successfully obtained JWT token",
                    username=username,
                    expires_in=expires_in,
                )

            except httpx.HTTPStatusError as e:
                logger.error(
                    "Failed to login to external API",
                    status_code=e.response.status_code,
                    detail=e.response.text,
                )
                raise
            except Exception as e:
                logger.error("Failed to fetch JWT token", error=str(e))
                raise

    async def get_authorized_client(self) -> httpx.AsyncClient:
        """Get an httpx client with authorization header."""
        token = await self.get_access_token()
        return httpx.AsyncClient(
            headers={"Authorization": f"Bearer {token}"},
            timeout=30.0,
        )


# Global auth client instance
auth_client = AuthClient()
