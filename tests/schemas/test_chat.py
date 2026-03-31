import pytest
from pydantic import ValidationError

from app.schemas.chat import ChatRequest, ChatMessage


def test_chat_request_with_valid_payload() -> None:
    request = ChatRequest(
        message=[{"role": "user", "content": "Hello"}],
        temperature=0.5,
        max_output_tokens=100,
    )

    assert request.message[0].role == "user"
    assert request.message[0].content == "Hello"
    assert request.temperature == 0.5
    assert request.max_output_tokens == 100


def test_chat_request_fails_when_messages_empty() -> None:
    with pytest.raises(ValidationError):
        ChatRequest(message=[])


def test_chat_request_fails_when_content_blank() -> None:
    with pytest.raises(ValidationError):
        ChatRequest(message=[{"role": "user", "content": "   "}])

def test_chat_message_trims_content() -> None:
    message = ChatMessage(role="user", content="   Hello  world ")
    assert message.content == "Hello  world"