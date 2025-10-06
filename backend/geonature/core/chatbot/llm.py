"""Client LLM configurable pour le chatbot GeoNature."""

from __future__ import annotations

from flask import current_app
import logging
import os
from typing import Any, Dict, Iterable, Optional

import requests

LOGGER = logging.getLogger(__name__)

DEFAULT_PROVIDER = "openai"
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_OPENAI_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_TIMEOUT = 60


class LLMConfigurationError(RuntimeError):
    """Configuration invalide ou manquante pour le LLM."""


class LLMClient:
    def __init__(self) -> None:
        self.provider = os.getenv("CHATBOT_LLM_PROVIDER", DEFAULT_PROVIDER).lower()
        self.timeout = int(os.getenv("CHATBOT_LLM_TIMEOUT", DEFAULT_TIMEOUT))
        LOGGER.info("Initialisation LLM provider=%s", self.provider)

    def _call_openai(
        self,
        messages: Iterable[Dict[str, Any]],
        *,
        functions: Optional[Iterable[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        api_key = os.getenv("OPENAI_API_KEY", current_app.config.get("OPENAI_API_KEY"))
        if not api_key:
            raise LLMConfigurationError("OPENAI_API_KEY est requis pour le provider OpenAI")
        model = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
        url = os.getenv("OPENAI_API_URL", DEFAULT_OPENAI_URL)

        payload: Dict[str, Any] = {
            "model": model,
            "messages": list(messages),
        }
        if functions:
            payload["tools"] = [
                {"type": "function", "function": fn} for fn in functions
            ]
            payload["tool_choice"] = "auto"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        LOGGER.debug("LLM OpenAI call model=%s tools=%s", model, bool(functions))

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=self.timeout,
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            LOGGER.error("Erreur OpenAI %s : %s", response.status_code, response.text)
            raise LLMConfigurationError(f"Erreur LLM: {response.status_code}") from exc
        return response.json()

    def invoke(
        self,
        messages: Iterable[Dict[str, Any]],
        *,
        functions: Optional[Iterable[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        if self.provider == "openai":
            return self._call_openai(messages, functions=functions)

        raise LLMConfigurationError(f"Provider LLM inconnu: {self.provider}")


llm_client = LLMClient()


def llm_completion(
    messages: Iterable[Dict[str, Any]],
    *,
    functions: Optional[Iterable[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Wrapper pratique autour du client global."""

    return llm_client.invoke(messages, functions=functions)
