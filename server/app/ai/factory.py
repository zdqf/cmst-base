"""AI adapter factory."""

from app.config import settings

from .base import AIAdapter
from .openai_adapter import OpenAIAdapter
from .private_adapter import PrivateModelAdapter


class AIAdapterFactory:
    """Factory for creating AI adapter instances based on configuration."""

    @staticmethod
    def create(provider: str | None = None) -> AIAdapter:
        """Create an AI adapter for the given provider.

        Args:
            provider: The provider name ("openai" or "private").
                      Defaults to settings.ai_provider if not specified.

        Returns:
            An AIAdapter instance for the requested provider.

        Raises:
            ValueError: If the provider is not supported.
        """
        provider = provider or settings.ai_provider

        if provider == "openai":
            return OpenAIAdapter()
        elif provider == "private":
            return PrivateModelAdapter()
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")
