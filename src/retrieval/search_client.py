"""
Azure AI Search retrieval client. Hybrid (vector + keyword) search with
semantic re-ranking, per data-indexing-plan.md §4. Index schema:
rag-index-schema.json.
"""

from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient as AzureSearchClient
from azure.core.credentials import AzureKeyCredential

from src.config import get_settings

settings = get_settings()


class SearchClient:
    def __init__(self) -> None:
        credential = (
            AzureKeyCredential(settings.azure_search_api_key)
            if settings.azure_search_api_key
            else DefaultAzureCredential()
        )
        self._client = AzureSearchClient(
            endpoint=settings.azure_search_endpoint,
            index_name=settings.azure_search_index_name,
            credential=credential,
        )

    def retrieve(
        self,
        query: str,
        county: str | None = None,
        top_k: int = 5,
    ) -> list[dict]:
        """
        Hybrid search with semantic re-ranking. Filters to `county` plus
        statewide (county eq null) results when county is provided,
        per data-indexing-plan.md §4.

        Returns chunks with their `citation` field so callers can ground
        generated responses and show sources.
        """
        raise NotImplementedError

    def embed_query(self, text: str) -> list[float]:
        """Generate the query embedding via Azure OpenAI embeddings deployment."""
        raise NotImplementedError
