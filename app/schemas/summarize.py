from typing import Literal

from pydantic import BaseModel, Field, field_validator


class SummarizeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=30000)
    style: Literal["executive", "bullet", "technical"] = "executive"
    max_bullets: int = Field(default=5, ge=1, le=10)
    target_language: Literal["uk", "en"] = "uk"

    @field_validator("text")
    @classmethod
    def validate_text_not_blank(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Text must not be blank or whitespace only.")
        return trimmed


class SummaryBullet(BaseModel):
    text: str = Field(min_length=1, max_length=1000)
    importance: Literal["high", "medium", "low"]


class SummarizeResponse(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    summary: str = Field(min_length=1, max_length=5000)
    bullets: list[SummaryBullet] = Field(default_factory=list, max_length=10)
    risks: list[str] = Field(default_factory=list, max_length=10)
    action_items: list[str] = Field(default_factory=list, max_length=10)
