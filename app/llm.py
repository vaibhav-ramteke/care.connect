"""Thin, fault-tolerant wrapper around the Anthropic Claude API.

The wrapper is deliberately best-effort: every call is guarded so that a
missing API key, a network error, an unsupported parameter, or any other
failure transparently returns ``None``. Callers treat ``None`` as "the LLM is
unavailable" and fall back to deterministic rule-based behaviour. This is what
makes the platform a true hybrid — smart when a key is present, fully
functional when it is not.
"""

from __future__ import annotations

import logging

from .config import Settings

logger = logging.getLogger("carepath.llm")


class LLMClient:
    def __init__(self, settings: Settings) -> None:
        self.model = settings.anthropic_model
        self._client = None
        self.enabled = False

        if not settings.anthropic_api_key:
            logger.info("No ANTHROPIC_API_KEY set — running in rule-based mode.")
            return

        try:
            from anthropic import Anthropic  # imported lazily so the package is optional

            self._client = Anthropic(api_key=settings.anthropic_api_key)
            self.enabled = True
            logger.info("LLM mode enabled (model=%s).", self.model)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Could not initialise Anthropic client: %s", exc)
            self.enabled = False

    # ------------------------------------------------------------------
    def _text_of(self, response) -> str | None:
        try:
            parts = [
                block.text
                for block in response.content
                if getattr(block, "type", None) == "text"
            ]
        except Exception:  # pragma: no cover - defensive
            return None
        text = "\n".join(parts).strip()
        return text or None

    # ------------------------------------------------------------------
    def complete(
        self,
        system: str,
        prompt: str,
        *,
        max_tokens: int = 1024,
        thinking: bool = False,
    ) -> str | None:
        """Generate free-text. Returns None if the LLM is unavailable/fails."""
        if not self.enabled or self._client is None:
            return None

        kwargs: dict = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": prompt}],
        }
        if thinking:
            # Adaptive thinking is the recommended mode on Claude 4.6+ models.
            kwargs["thinking"] = {"type": "adaptive"}

        try:
            response = self._client.messages.create(**kwargs)
        except Exception as exc:
            logger.warning("LLM completion failed, falling back: %s", exc)
            return None
        return self._text_of(response)

    # ------------------------------------------------------------------
    def classify(self, message: str, labels: list[str]) -> str | None:
        """Pick exactly one label for the message, or None on failure."""
        if not self.enabled or self._client is None:
            return None

        system = (
            "You are an intent classifier for a hospital patient-engagement "
            "assistant. Reply with EXACTLY ONE label from the provided list and "
            "nothing else."
        )
        prompt = (
            "Allowed labels:\n"
            + "\n".join(f"- {label}" for label in labels)
            + f'\n\nPatient message: "{message}"\n\nLabel:'
        )
        out = self.complete(system, prompt, max_tokens=20)
        if not out:
            return None

        out_lower = out.strip().lower()
        # Exact match first, then substring containment.
        for label in labels:
            if out_lower == label.lower():
                return label
        for label in labels:
            if label.lower() in out_lower:
                return label
        return None
