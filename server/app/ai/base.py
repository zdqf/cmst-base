"""Abstract base class for AI adapters."""

from abc import ABC, abstractmethod


class AIAdapter(ABC):
    """Base class for AI model adapters.

    All AI adapters must implement the `generate` method to provide
    a unified interface for text generation across different providers.
    """

    @abstractmethod
    async def generate(self, prompt: str, context: dict | None = None) -> str:
        """Generate text from the AI model.

        Args:
            prompt: The input prompt for the AI model.
            context: Optional additional context for the generation.

        Returns:
            The generated text response.
        """
