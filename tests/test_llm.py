"""Unit tests for the fault-tolerant LLM wrapper.

The wrapper's contract: it must NEVER raise. Any failure (no key, network
error, bad response) returns None so callers fall back to deterministic logic.
"""

from __future__ import annotations

import types

import pytest

from app.config import Settings
from app.llm import LLMClient

pytestmark = pytest.mark.unit


def test_disabled_without_api_key():
    llm = LLMClient(Settings(anthropic_api_key=None))
    assert llm.enabled is False
    assert llm.complete("sys", "prompt") is None
    assert llm.classify("hello", ["general", "doctor_search"]) is None


def test_text_of_extracts_text_blocks():
    llm = LLMClient(Settings(anthropic_api_key=None))
    response = types.SimpleNamespace(
        content=[
            types.SimpleNamespace(type="text", text="Hello"),
            types.SimpleNamespace(type="thinking", text="ignored"),
            types.SimpleNamespace(type="text", text="world"),
        ]
    )
    assert llm._text_of(response) == "Hello\nworld"


def test_text_of_returns_none_for_empty():
    llm = LLMClient(Settings(anthropic_api_key=None))
    response = types.SimpleNamespace(content=[])
    assert llm._text_of(response) is None


def test_text_of_is_defensive_against_bad_response():
    llm = LLMClient(Settings(anthropic_api_key=None))
    # content is None -> iterating raises internally -> None, never an exception.
    assert llm._text_of(types.SimpleNamespace(content=None)) is None


def test_complete_swallows_client_errors(monkeypatch):
    """An exception from the underlying client must become a None return."""
    llm = LLMClient(Settings(anthropic_api_key=None))

    class Boom:
        class messages:
            @staticmethod
            def create(**kwargs):
                raise RuntimeError("network down")

    # Force-enable with a stub client that always blows up.
    llm.enabled = True
    llm._client = Boom()
    assert llm.complete("sys", "prompt") is None


def test_classify_maps_response_to_label(monkeypatch):
    llm = LLMClient(Settings(anthropic_api_key=None))
    llm.enabled = True
    llm._client = object()  # not used because we stub complete()
    monkeypatch.setattr(llm, "complete", lambda *a, **k: "doctor_search")
    assert llm.classify("which doctor?", ["general", "doctor_search"]) == "doctor_search"


def test_classify_handles_unmatched_response(monkeypatch):
    llm = LLMClient(Settings(anthropic_api_key=None))
    llm.enabled = True
    llm._client = object()
    monkeypatch.setattr(llm, "complete", lambda *a, **k: "something else entirely")
    assert llm.classify("hi", ["general", "doctor_search"]) is None
