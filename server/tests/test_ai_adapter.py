"""Unit tests for AI adapters and factory (Task 4.4).

Validates: Requirement 18.4
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.ai.base import AIAdapter
from app.ai.factory import AIAdapterFactory
from app.ai.openai_adapter import OpenAIAdapter
from app.ai.private_adapter import PrivateModelAdapter


# ---------------------------------------------------------------------------
# 1. AIAdapter is abstract and cannot be instantiated directly
# ---------------------------------------------------------------------------


class TestAIAdapterBase:
    def test_cannot_instantiate_abstract_class(self):
        with pytest.raises(TypeError):
            AIAdapter()

    def test_subclass_must_implement_generate(self):
        class IncompleteAdapter(AIAdapter):
            pass

        with pytest.raises(TypeError):
            IncompleteAdapter()

    def test_concrete_subclass_can_be_instantiated(self):
        class ConcreteAdapter(AIAdapter):
            async def generate(self, prompt: str, context: dict | None = None) -> str:
                return "ok"

        adapter = ConcreteAdapter()
        assert isinstance(adapter, AIAdapter)


# ---------------------------------------------------------------------------
# 2. OpenAIAdapter
# ---------------------------------------------------------------------------


class TestOpenAIAdapter:
    @patch("app.ai.openai_adapter.settings")
    def test_init_uses_settings(self, mock_settings):
        mock_settings.openai_api_key = "test-key"
        mock_settings.openai_model = "gpt-4o-mini"

        with patch("app.ai.openai_adapter.AsyncOpenAI") as mock_client_cls:
            adapter = OpenAIAdapter()
            mock_client_cls.assert_called_once_with(api_key="test-key")
            assert adapter._model == "gpt-4o-mini"

    @pytest.mark.asyncio
    @patch("app.ai.openai_adapter.settings")
    async def test_generate_calls_chat_completions(self, mock_settings):
        mock_settings.openai_api_key = "test-key"
        mock_settings.openai_model = "gpt-4o-mini"

        mock_message = MagicMock()
        mock_message.content = "AI response"
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        with patch("app.ai.openai_adapter.AsyncOpenAI") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            adapter = OpenAIAdapter()
            result = await adapter.generate("hello")

            assert result == "AI response"
            mock_client.chat.completions.create.assert_called_once_with(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "hello"}],
            )

    @pytest.mark.asyncio
    @patch("app.ai.openai_adapter.settings")
    async def test_generate_with_system_context(self, mock_settings):
        mock_settings.openai_api_key = "test-key"
        mock_settings.openai_model = "gpt-4o-mini"

        mock_message = MagicMock()
        mock_message.content = "response with system"
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        with patch("app.ai.openai_adapter.AsyncOpenAI") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            adapter = OpenAIAdapter()
            result = await adapter.generate("hello", context={"system": "You are a helper"})

            assert result == "response with system"
            mock_client.chat.completions.create.assert_called_once_with(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helper"},
                    {"role": "user", "content": "hello"},
                ],
            )

    @pytest.mark.asyncio
    @patch("app.ai.openai_adapter.settings")
    async def test_generate_returns_empty_on_none_content(self, mock_settings):
        mock_settings.openai_api_key = "test-key"
        mock_settings.openai_model = "gpt-4o-mini"

        mock_message = MagicMock()
        mock_message.content = None
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        with patch("app.ai.openai_adapter.AsyncOpenAI") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            adapter = OpenAIAdapter()
            result = await adapter.generate("hello")
            assert result == ""


# ---------------------------------------------------------------------------
# 3. PrivateModelAdapter
# ---------------------------------------------------------------------------


class TestPrivateModelAdapter:
    @patch("app.ai.private_adapter.settings")
    def test_init_uses_settings(self, mock_settings):
        mock_settings.private_model_endpoint = "https://model.example.com/generate"
        mock_settings.private_model_api_key = "private-key"

        adapter = PrivateModelAdapter()
        assert adapter._endpoint == "https://model.example.com/generate"
        assert adapter._api_key == "private-key"

    @pytest.mark.asyncio
    @patch("app.ai.private_adapter.settings")
    async def test_generate_sends_post_request(self, mock_settings):
        mock_settings.private_model_endpoint = "https://model.example.com/generate"
        mock_settings.private_model_api_key = "private-key"

        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "private response"}
        mock_response.raise_for_status = MagicMock()

        with patch("app.ai.private_adapter.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            adapter = PrivateModelAdapter()
            result = await adapter.generate("hello")

            assert result == "private response"
            mock_client.post.assert_called_once_with(
                "https://model.example.com/generate",
                json={"prompt": "hello"},
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer private-key",
                },
                timeout=60.0,
            )

    @pytest.mark.asyncio
    @patch("app.ai.private_adapter.settings")
    async def test_generate_with_context(self, mock_settings):
        mock_settings.private_model_endpoint = "https://model.example.com/generate"
        mock_settings.private_model_api_key = "key"

        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "ctx response"}
        mock_response.raise_for_status = MagicMock()

        with patch("app.ai.private_adapter.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            adapter = PrivateModelAdapter()
            result = await adapter.generate("hello", context={"system": "role"})

            assert result == "ctx response"
            call_kwargs = mock_client.post.call_args
            assert call_kwargs.kwargs["json"] == {
                "prompt": "hello",
                "context": {"system": "role"},
            }

    @pytest.mark.asyncio
    @patch("app.ai.private_adapter.settings")
    async def test_generate_no_api_key_omits_auth_header(self, mock_settings):
        mock_settings.private_model_endpoint = "https://model.example.com/generate"
        mock_settings.private_model_api_key = ""

        mock_response = MagicMock()
        mock_response.json.return_value = {"text": "fallback field"}
        mock_response.raise_for_status = MagicMock()

        with patch("app.ai.private_adapter.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            adapter = PrivateModelAdapter()
            result = await adapter.generate("hello")

            assert result == "fallback field"
            call_kwargs = mock_client.post.call_args
            assert "Authorization" not in call_kwargs.kwargs["headers"]


# ---------------------------------------------------------------------------
# 4. AIAdapterFactory
# ---------------------------------------------------------------------------


class TestAIAdapterFactory:
    @patch("app.ai.factory.settings")
    def test_create_openai_adapter(self, mock_settings):
        mock_settings.ai_provider = "openai"
        mock_settings.openai_api_key = "key"
        mock_settings.openai_model = "gpt-4o-mini"

        adapter = AIAdapterFactory.create("openai")
        assert isinstance(adapter, OpenAIAdapter)

    @patch("app.ai.factory.settings")
    def test_create_private_adapter(self, mock_settings):
        mock_settings.ai_provider = "private"
        mock_settings.private_model_endpoint = "https://example.com"
        mock_settings.private_model_api_key = "key"

        adapter = AIAdapterFactory.create("private")
        assert isinstance(adapter, PrivateModelAdapter)

    @patch("app.ai.factory.settings")
    def test_create_uses_settings_default(self, mock_settings):
        mock_settings.ai_provider = "openai"
        mock_settings.openai_api_key = "key"
        mock_settings.openai_model = "gpt-4o-mini"

        adapter = AIAdapterFactory.create()
        assert isinstance(adapter, OpenAIAdapter)

    @patch("app.ai.factory.settings")
    def test_create_unsupported_provider_raises(self, mock_settings):
        mock_settings.ai_provider = "unknown"

        with pytest.raises(ValueError, match="Unsupported AI provider: unknown"):
            AIAdapterFactory.create("unknown")
