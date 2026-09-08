import hashlib
import os
import time
from typing import List, Optional

from dotenv import load_dotenv

from models import ChatMessage

load_dotenv()


class LLMNotConfigured(Exception):
    """Raised when GEMINI_API_KEY is missing or the client failed to init."""


class GeminiService:
    """Gemini LLM wrapper with retry, response cache, and a simple rate limit."""

    def __init__(self):
        self.api_key = (os.getenv("GEMINI_API_KEY") or "").strip()
        self.model = None
        self._backend = None
        self._client = None
        self._cache: dict[str, str] = {}
        self._last_call = 0.0
        self._min_interval = 0.4
        if self.api_key:
            self._init_client()

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.model)

    def _init_client(self) -> None:
        try:
            from google import genai

            self._client = genai.Client(api_key=self.api_key)
            self.model = "gemini-3.6-flash"
            self._backend = "genai"
            return
        except Exception:
            pass
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-3.6-flash")
            self._backend = "generativeai"
        except Exception:
            self.model = None
            self._backend = None

    def generate_response(
        self,
        message: str,
        history: List[ChatMessage],
        system_prompt: Optional[str] = None,
    ) -> str:
        if not self.is_configured:
            raise LLMNotConfigured("LLM not configured")

        cache_key = hashlib.sha256(
            f"{system_prompt or ''}|{message}|{[ (m.role, m.content) for m in history ]}".encode()
        ).hexdigest()
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        last_error = None
        for attempt in range(3):
            try:
                self._throttle()
                text = self._call_model(message, history, system_prompt)
                if len(self._cache) > 128:
                    self._cache.pop(next(iter(self._cache)))
                self._cache[cache_key] = text
                return text
            except Exception as exc:
                last_error = exc
                time.sleep(0.4 * (attempt + 1))

        raise last_error or RuntimeError("LLM request failed")

    def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_call
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_call = time.monotonic()

    def _call_model(
        self,
        message: str,
        history: List[ChatMessage],
        system_prompt: Optional[str],
    ) -> str:
        if self._backend == "genai":
            contents = []
            if system_prompt:
                contents.append(f"System: {system_prompt}")
            for msg in history:
                contents.append(f"{msg.role}: {msg.content}")
            contents.append(f"user: {message}")
            response = self._client.models.generate_content(
                model=self.model,
                contents="\n".join(contents),
            )
            return (response.text or "").strip() or "No response from the model."

        formatted_history = [
            {
                "role": "user" if msg.role == "user" else "model",
                "parts": [msg.content],
            }
            for msg in history
        ]
        prompt = message if not system_prompt else f"{system_prompt}\n\n{message}"
        chat = self.model.start_chat(history=formatted_history)
        response = chat.send_message(prompt)
        return (response.text or "").strip() or "No response from the model."
