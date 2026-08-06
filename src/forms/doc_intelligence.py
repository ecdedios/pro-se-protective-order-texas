"""
Document Intelligence client — scoped to parsing survivor-uploaded
supporting documents (e.g. police reports, prior orders), NOT the blank
protective order form itself. See architecture doc §3.4 for why this
scope boundary is deliberate.
"""

from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient as AzureDIClient

from src.config import get_settings

settings = get_settings()


class DocumentIntelligenceClient:
    def __init__(self) -> None:
        credential = (
            AzureKeyCredential(settings.azure_document_intelligence_api_key)
            if settings.azure_document_intelligence_api_key
            else DefaultAzureCredential()
        )
        self._client = AzureDIClient(
            endpoint=settings.azure_document_intelligence_endpoint,
            credential=credential,
        )

    def extract_supporting_facts(self, file_bytes: bytes) -> dict:
        """
        Parses an uploaded supporting document (e.g. police report) using
        the prebuilt-document model and extracts relevant facts/dates for
        merging into intake data. Does not touch the blank protective
        order form template — see field_map.py for that.
        """
        raise NotImplementedError
