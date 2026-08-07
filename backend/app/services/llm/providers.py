"""LLM provider adapters.

``LLMService`` is the only place a provider is touched, so Gemini can be swapped for or added
alongside the UF NaviGator endpoint without changing a route or a component.
"""

from __future__ import annotations

import asyncio
import json
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import settings
from app.core.errors import ModelUnavailable
from app.core.logging import get_logger

log = get_logger("aipassport.llm")


@dataclass(slots=True)
class ChatMessage:
    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass(slots=True)
class Completion:
    content: str
    model: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    latency_ms: int | None = None


class LLMProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def complete(
        self,
        messages: list[ChatMessage],
        *,
        max_output_tokens: int,
        temperature: float,
        json_mode: bool,
    ) -> Completion: ...


class EchoProvider(LLMProvider):
    """Deterministic stub used when no credential is configured."""

    name = "echo"

    def __init__(self, model: str = "offline-stub") -> None:
        self.model = model

    async def complete(
        self,
        messages: list[ChatMessage],
        *,
        max_output_tokens: int,
        temperature: float,
        json_mode: bool,
    ) -> Completion:
        del max_output_tokens, temperature
        last = next((m.content for m in reversed(messages) if m.role == "user"), "")
        if json_mode:
            content = json.dumps({"echo": last[:500]})
        else:
            content = last[:500]
        return Completion(content=content, model=self.model, latency_ms=0)


class _HttpProvider(LLMProvider):
    def __init__(self, *, timeout: float) -> None:
        self._timeout = timeout

    async def _post_with_retry(self, url: str, *, headers: dict[str, str], payload: dict[str, Any]) -> dict[str, Any]:
        attempts = 3
        last_error: str = "unknown"
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            for attempt in range(attempts):
                try:
                    response = await client.post(url, headers=headers, json=payload)
                except httpx.TimeoutException:
                    last_error = "timeout"
                except httpx.HTTPError as exc:
                    last_error = f"transport:{type(exc).__name__}"
                else:
                    if response.status_code < 400:
                        return response.json()
                    last_error = f"http_{response.status_code}"
                    if response.status_code not in (408, 429, 500, 502, 503, 504):
                        log.warning(
                            "llm_request_failed",
                            provider=self.name,
                            status=response.status_code,
                            body=response.text[:200],
                        )
                        raise ModelUnavailable()
                if attempt < attempts - 1:
                    await asyncio.sleep((2**attempt) * 0.7 + random.random() * 0.3)
        log.warning("llm_request_exhausted", provider=self.name, error=last_error)
        raise ModelUnavailable()


class OpenAICompatibleProvider(_HttpProvider):
    """Works with the UF NaviGator Toolkit, OpenAI, and any OpenAI-compatible gateway."""

    name = "openai_compatible"

    def __init__(self, *, base_url: str, api_key: str, model: str, timeout: float) -> None:
        super().__init__(timeout=timeout)
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    async def complete(
        self,
        messages: list[ChatMessage],
        *,
        max_output_tokens: int,
        temperature: float,
        json_mode: bool,
    ) -> Completion:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_output_tokens,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        started = time.perf_counter()
        data = await self._post_with_retry(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            payload=payload,
        )
        latency_ms = int((time.perf_counter() - started) * 1000)

        try:
            content = data["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError) as exc:
            log.warning("llm_bad_shape", provider=self.name)
            raise ModelUnavailable() from exc

        usage = data.get("usage") or {}
        return Completion(
            content=content,
            model=data.get("model") or self.model,
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            latency_ms=latency_ms,
        )


class GeminiProvider(_HttpProvider):
    name = "gemini"

    def __init__(self, *, api_key: str, model: str, timeout: float) -> None:
        super().__init__(timeout=timeout)
        self.api_key = api_key
        self.model = model

    async def complete(
        self,
        messages: list[ChatMessage],
        *,
        max_output_tokens: int,
        temperature: float,
        json_mode: bool,
    ) -> Completion:
        system_parts = [m.content for m in messages if m.role == "system"]
        contents = [
            {
                "role": "model" if m.role == "assistant" else "user",
                "parts": [{"text": m.content}],
            }
            for m in messages
            if m.role != "system"
        ]
        payload: dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_output_tokens,
            },
        }
        if system_parts:
            payload["systemInstruction"] = {"parts": [{"text": "\n\n".join(system_parts)}]}
        if json_mode:
            payload["generationConfig"]["responseMimeType"] = "application/json"

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent"
        )
        started = time.perf_counter()
        data = await self._post_with_retry(
            url, headers={"x-goog-api-key": self.api_key}, payload=payload
        )
        latency_ms = int((time.perf_counter() - started) * 1000)

        try:
            parts = data["candidates"][0]["content"]["parts"]
            content = "".join(p.get("text", "") for p in parts)
        except (KeyError, IndexError, TypeError) as exc:
            log.warning("llm_bad_shape", provider=self.name)
            raise ModelUnavailable() from exc

        usage = data.get("usageMetadata") or {}
        return Completion(
            content=content,
            model=self.model,
            prompt_tokens=usage.get("promptTokenCount"),
            completion_tokens=usage.get("candidatesTokenCount"),
            latency_ms=latency_ms,
        )


def build_provider() -> LLMProvider:
    choice = settings.LLM_PROVIDER
    timeout = settings.LLM_TIMEOUT_SECONDS

    if choice == "echo":
        return EchoProvider()
    if choice == "gemini" or (
        choice == "auto" and not settings.LLM_API_KEY and settings.GEMINI_API_KEY
    ):
        if not settings.GEMINI_API_KEY:
            log.warning("llm_missing_key", provider="gemini")
            return EchoProvider()
        return GeminiProvider(
            api_key=settings.GEMINI_API_KEY, model=settings.GEMINI_MODEL, timeout=timeout
        )
    if choice in ("openai_compatible", "auto"):
        if settings.LLM_API_KEY and settings.LLM_BASE_URL:
            return OpenAICompatibleProvider(
                base_url=settings.LLM_BASE_URL,
                api_key=settings.LLM_API_KEY,
                model=settings.LLM_MODEL,
                timeout=timeout,
            )
        if choice == "openai_compatible":
            log.warning("llm_missing_key", provider="openai_compatible")
        return EchoProvider()
    return EchoProvider()
