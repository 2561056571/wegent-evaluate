"""
Configuration endpoint for exposing non-sensitive settings to frontend.
"""
from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings
from app.core.runtime_config import (
    get_external_api_base_url,
    set_external_api_base_url as _set_external_api_base_url,
    get_external_api_username,
    set_external_api_username as _set_external_api_username,
    get_external_api_password,
    set_external_api_password as _set_external_api_password,
)

router = APIRouter()


class SyncConfigResponse(BaseModel):
    """Sync configuration response schema."""

    external_api_base_url: str
    external_api_username: str
    sync_cron_expression: str


class EvaluationConfigResponse(BaseModel):
    """Evaluation configuration response schema."""

    ragas_llm_model: str
    ragas_embedding_model: str
    evaluation_cron_expression: str
    evaluation_batch_size: int


class SettingsConfigResponse(BaseModel):
    """Combined settings configuration response schema."""

    sync: SyncConfigResponse
    evaluation: EvaluationConfigResponse


class SetExternalApiBaseUrlRequest(BaseModel):
    """Request schema for setting external API base URL."""

    external_api_base_url: str


class SetExternalApiBaseUrlResponse(BaseModel):
    """Response schema for setting external API base URL."""

    success: bool
    message: str
    external_api_base_url: str


class SetExternalApiCredentialsRequest(BaseModel):
    """Request schema for setting external API credentials."""

    username: str
    password: str


class SetExternalApiCredentialsResponse(BaseModel):
    """Response schema for setting external API credentials."""

    success: bool
    message: str
    username: str


@router.get("/config", response_model=SettingsConfigResponse)
async def get_settings_config():
    """
    Get application configuration for display in settings page.

    Returns non-sensitive configuration values that can be safely
    exposed to the frontend.
    """
    return SettingsConfigResponse(
        sync=SyncConfigResponse(
            external_api_base_url=get_external_api_base_url(),
            external_api_username=get_external_api_username(),
            sync_cron_expression=settings.SYNC_CRON_EXPRESSION,
        ),
        evaluation=EvaluationConfigResponse(
            ragas_llm_model=settings.RAGAS_LLM_MODEL,
            ragas_embedding_model=settings.RAGAS_EMBEDDING_MODEL,
            evaluation_cron_expression=settings.EVALUATION_CRON_EXPRESSION,
            evaluation_batch_size=settings.EVALUATION_BATCH_SIZE,
        ),
    )


@router.post("/external-api-base-url", response_model=SetExternalApiBaseUrlResponse)
async def set_external_api_base_url(request: SetExternalApiBaseUrlRequest):
    """
    Set the external API base URL at runtime.
    
    This configuration is stored in memory only and will be reset when the server restarts.
    The new URL takes effect immediately for subsequent sync operations.
    """
    url = request.external_api_base_url.strip()
    
    # Basic URL validation
    if not url:
        return SetExternalApiBaseUrlResponse(
            success=False,
            message="URL cannot be empty",
            external_api_base_url=get_external_api_base_url(),
        )
    
    if not url.startswith(("http://", "https://")):
        return SetExternalApiBaseUrlResponse(
            success=False,
            message="URL must start with http:// or https://",
            external_api_base_url=get_external_api_base_url(),
        )
    
    # Remove trailing slash for consistency
    url = url.rstrip("/")
    
    # Store in runtime config
    _set_external_api_base_url(url)
    
    return SetExternalApiBaseUrlResponse(
        success=True,
        message="External API base URL updated successfully. This change is temporary and will be reset on server restart.",
        external_api_base_url=url,
    )


@router.post("/external-api-credentials", response_model=SetExternalApiCredentialsResponse)
async def set_external_api_credentials(request: SetExternalApiCredentialsRequest):
    """
    Set the external API credentials (username and password) at runtime.
    
    This configuration is stored in memory only and will be reset when the server restarts.
    The new credentials take effect immediately for subsequent sync operations.
    """
    username = request.username.strip()
    password = request.password
    
    # Basic validation
    if not username:
        return SetExternalApiCredentialsResponse(
            success=False,
            message="Username cannot be empty",
            username=get_external_api_username(),
        )
    
    if not password:
        return SetExternalApiCredentialsResponse(
            success=False,
            message="password cannot be empty",
            username=get_external_api_username(),
        )
    
    # Store in runtime config
    _set_external_api_username(username)
    _set_external_api_password(password)
    
    return SetExternalApiCredentialsResponse(
        success=True,
        message="External API credentials updated successfully. This change is temporary and will be reset on server restart.",
        username=username,
    )
