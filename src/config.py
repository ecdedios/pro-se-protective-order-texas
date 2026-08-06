"""
App configuration. Values load from environment / .env locally, and from
the Container App's configured env vars (populated via Key Vault references)
in Azure. Auth to Azure services uses DefaultAzureCredential (managed
identity) — see architecture doc §3.5.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "local"
    log_level: str = "INFO"

    azure_openai_endpoint: str
    azure_openai_deployment_name: str
    azure_openai_api_version: str = "2024-10-21"

    azure_search_endpoint: str
    azure_search_index_name: str = "tx-protective-order-corpus"

    azure_document_intelligence_endpoint: str

    azure_key_vault_url: str | None = None

    # Local-dev-only fallback. Never set in deployed environments —
    # production auth goes through managed identity.
    azure_openai_api_key: str | None = None
    azure_search_api_key: str | None = None
    azure_document_intelligence_api_key: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
