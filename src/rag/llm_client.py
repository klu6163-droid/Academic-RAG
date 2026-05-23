"""
Unified LLM client abstraction.
Supports OpenAI-compatible APIs.
Uses threading-based timeout as fallback for SDK timeout.
"""

import json
import os
from typing import Any


class LLMClient:
    def __init__(self, config):
        self.api_key = config.api_key
        self.base_url = config.base_url
        self.model = config.model
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens
        self.timeout = config.timeout

    @property
    def is_available(self) -> bool:
        return bool(self.api_key)

    def _call_api(self, messages: list[dict], json_mode: bool = False) -> str:
        """Actual API call (runs in thread)."""
        from openai import OpenAI

        kwargs: dict[str, Any] = {"api_key": self.api_key, "timeout": self.timeout}
        if self.base_url:
            kwargs["base_url"] = self.base_url

        client = OpenAI(**kwargs)

        call_kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        if json_mode:
            call_kwargs["response_format"] = {"type": "json_object"}

        resp = client.chat.completions.create(**call_kwargs)
        return resp.choices[0].message.content

    def chat(self, messages: list[dict], json_mode: bool = False) -> str:
        """Send chat completion request with threading-based timeout fallback."""
        if not self.is_available:
            raise RuntimeError("LLM API key not configured. Set LLM_API_KEY or OPENAI_API_KEY in .env")

        import threading

        result: list[Any] = [None]
        error: list[Exception] = [None]

        def target():
            try:
                result[0] = self._call_api(messages, json_mode)
            except Exception as e:
                error[0] = e

        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        thread.join(timeout=self.timeout + 10)  # Extra buffer beyond SDK timeout

        if thread.is_alive():
            # Thread still running — force timeout
            raise TimeoutError(f"LLM request timed out after {self.timeout}s (thread timeout)")

        if error[0] is not None:
            raise error[0]

        return result[0]

    def chat_json(self, messages: list[dict]) -> dict:
        """Send chat completion and parse JSON response."""
        text = self.chat(messages, json_mode=True)
        if not text:
            return {"answer": "", "confidence": "Low", "no_answer": True, "evidence_levels": {}, "cited_evidence": [], "warnings": ["LLM returned empty response"]}
        return json.loads(text)
