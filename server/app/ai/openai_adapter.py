"""OpenAI adapter implementation."""

from openai import AsyncOpenAI

from app.config import settings

from .base import AIAdapter


class OpenAIAdapter(AIAdapter):
    """AI adapter that uses the OpenAI API for text generation."""

    def __init__(self) -> None:
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model

    async def generate(self, prompt: str, context: dict | None = None) -> str:
        """Generate text using OpenAI chat completions API.

        Args:
            prompt: The user prompt to send to the model.
            context: Optional context; if it contains a 'system' key,
                     that value is used as the system message.

        Returns:
            The generated text from the model.
        """
        messages: list[dict[str, str]] = []

        if context and "system" in context:
            messages.append({"role": "system", "content": context["system"]})

        messages.append({"role": "user", "content": prompt})

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
        )

        return response.choices[0].message.content or ""
