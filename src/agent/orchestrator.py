"""
Agent orchestrator: manages intake conversation state, decides next
question, classifies case type, and requests grounded answers via RAG
retrieval. See architecture doc §3.2.
"""

from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from src.config import get_settings
from src.agent.guardrails import SYSTEM_SCOPE_INSTRUCTIONS
from src.retrieval.search_client import SearchClient

settings = get_settings()


def build_openai_client() -> AzureOpenAI:
    """
    Uses managed identity (DefaultAzureCredential) in Azure; falls back to
    an API key only if explicitly set for local development.
    """
    if settings.azure_openai_api_key:
        return AzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
        )

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://cognitiveservices.azure.com/.default",
    )
    return AzureOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        azure_ad_token_provider=token_provider,
        api_version=settings.azure_openai_api_version,
    )


class IntakeOrchestrator:
    """
    Drives the guided intake conversation: tracks collected fields,
    determines the next question, classifies case type once enough
    information is gathered, and routes procedural questions through
    the RAG retrieval client rather than answering from model memory.
    """

    def __init__(self) -> None:
        self.client = build_openai_client()
        self.search = SearchClient()

    def next_question(self, conversation_state: dict) -> dict:
        """Determine the next intake question given current state."""
        raise NotImplementedError

    def classify_case_type(self, conversation_state: dict) -> str:
        """Return one of: family_violence, dating_violence, stalking."""
        raise NotImplementedError

    def answer_procedural_question(self, question: str, county: str | None) -> dict:
        """
        Retrieve grounded context via SearchClient, then generate a
        response constrained to that context. Must not answer without
        retrieved support — see guardrails.is_grounded_response.
        """
        raise NotImplementedError
