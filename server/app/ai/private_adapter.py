"""Private model adapter implementation."""

import httpx

from app.config import settings

from .base import AIAdapter


class PrivateModelAdapter(AIAdapter):
    """AI adapter that calls a private model endpoint via HTTP."""

    def __init__(self) -> None:
        self._endpoint = settings.private_model_endpoint
        self._api_key = settings.private_model_api_key

    async def generate(self, prompt: str, context: dict | None = None) -> str:
        """Generate text by calling the private model endpoint.

        Sends a POST request with the prompt and optional context
        in the JSON body.

        Args:
            prompt: The input prompt for the model.
            context: Optional additional context passed in the request body.

        Returns:
            The generated text from the private model.
        """
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        payload: dict = {"prompt": prompt}
        if context:
            payload["context"] = context

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self._endpoint,
                json=payload,
                headers=headers,
                timeout=60.0,
            )
            response.raise_for_status()

        data = response.json()
        return data.get("result", data.get("text", ""))
