import json
from typing import Any

from openai import AsyncOpenAI

from app.core.config import Settings
from app.providers.base import (
    ProviderChatRequest,
    ProviderStructuredResult,
    ProviderSummarizeRequest,
    ProviderTextResult,
)
from app.schemas.chat import UsageInfo


SUMMARY_RESPONSE_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "summary": {"type": "string"},
        "bullets": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "importance": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                    },
                },
                "required": ["text", "importance"],
                "additionalProperties": False,
            },
        },
        "risks": {
            "type": "array",
            "items": {"type": "string"},
        },
        "action_items": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": ["title", "summary", "bullets", "risks", "action_items"],
    "additionalProperties": False,
}


class OpenAIProvider:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._client = AsyncOpenAI(api_key=self._settings.openai_api_key)

    @staticmethod
    def _build_input_messages(messages: list[tuple[str, str]]) -> list[dict[str, Any]]:
        return [
            {
                "role": role,
                "content": [
                    {
                        "type": "input_text",
                        "text": text,
                    }
                ],
            }
            for role, text in messages
        ]

    @staticmethod
    def _extract_usage(response: Any) -> UsageInfo | None:
        if getattr(response, "usage", None) is None:
            return None

        return UsageInfo(
            input_tokens=getattr(response.usage, "input_tokens", None),
            output_tokens=getattr(response.usage, "output_tokens", None),
            total_tokens=getattr(response.usage, "total_tokens", None),
        )

    async def chat(self, request: ProviderChatRequest) -> ProviderTextResult:
        input_messages = self._build_input_messages(
            [(message.role, message.content) for message in request.messages]
        )

        create_kwargs: dict[str, Any] = {
            "model": request.model,
            "input": input_messages,
        }

        if request.temperature is not None:
            create_kwargs["temperature"] = request.temperature

        if request.max_output_tokens is not None:
            create_kwargs["max_output_tokens"] = request.max_output_tokens

        response = await self._client.responses.create(**create_kwargs)

        return ProviderTextResult(
            content=(response.output_text or "").strip(),
            model=request.model,
            request_id=getattr(response, "id", None),
            usage=self._extract_usage(response),
        )

    async def summarize(self, request: ProviderSummarizeRequest) -> ProviderStructuredResult:
        input_messages = self._build_input_messages(
            [
                ("system", request.instructions),
                ("user", request.text),
            ]
        )

        response = await self._client.responses.create(
            model=request.model,
            input=input_messages,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "summarize_response",
                    "schema": SUMMARY_RESPONSE_JSON_SCHEMA,
                    "strict": True,
                }
            },
        )

        raw_output = (response.output_text or "").strip()
        if not raw_output:
            raise RuntimeError("Provider returned empty structured summarize content.")

        try:
            data = json.loads(raw_output)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Provider returned invalid JSON for summarize response."
            ) from exc

        return ProviderStructuredResult(
            data=data,
            model=request.model,
            request_id=getattr(response, "id", None),
            usage=self._extract_usage(response),
        )