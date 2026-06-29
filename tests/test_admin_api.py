"""Tests for the admin/staff endpoints: handoff queue, audit log, stats."""

from __future__ import annotations

import pytest

from tests.conftest import chat

pytestmark = pytest.mark.integration


# --------------------------------------------------------------------------- #
# Handoff queue
# --------------------------------------------------------------------------- #
def test_handoffs_empty_initially(client):
    body = client.get("/api/admin/handoffs").json()
    assert body["count"] == 0
    assert body["handoffs"] == []


def test_handoff_queue_records_escalations(client):
    chat(client, "I want to speak to a human about my bill")
    body = client.get("/api/admin/handoffs").json()
    assert body["count"] == 1
    assert body["handoffs"][0]["status"] == "open"


# --------------------------------------------------------------------------- #
# Audit log
# --------------------------------------------------------------------------- #
def test_audit_log_records_each_turn(client):
    chat(client, "I have knee pain")
    chat(client, "Book an appointment with Dr. Kulkarni")
    body = client.get("/api/admin/audit").json()
    assert body["count"] == 2


def test_audit_log_is_most_recent_first(client):
    chat(client, "I have knee pain")
    chat(client, "Can you show me my bill?")
    audit = client.get("/api/admin/audit").json()["audit"]
    assert audit[0]["intent"] == "billing_query"
    assert audit[1]["intent"] == "symptom_guidance"


def test_audit_log_respects_limit(client):
    for _ in range(3):
        chat(client, "I have knee pain")
    body = client.get("/api/admin/audit", params={"limit": 2}).json()
    assert body["count"] == 2


def test_emergency_is_flagged_in_audit(client):
    chat(client, "I have chest pain")
    audit = client.get("/api/admin/audit").json()["audit"]
    assert audit[0]["emergency"] is True
    assert audit[0]["red_flag"] == "chest pain"


# --------------------------------------------------------------------------- #
# Stats
# --------------------------------------------------------------------------- #
def test_stats_empty_initially(client):
    body = client.get("/api/admin/stats").json()
    assert body["total_conversations"] == 0
    assert body["total_messages"] == 0
    assert body["emergency_escalations"] == 0
    assert body["intent_breakdown"] == {}


def test_stats_aggregate_across_conversations(client):
    chat(client, "I have knee pain")
    chat(client, "I have chest pain")  # emergency
    chat(client, "Can you show me my bill?")

    body = client.get("/api/admin/stats").json()
    assert body["total_conversations"] == 3
    assert body["total_messages"] == 3
    assert body["emergency_escalations"] == 1
    assert body["open_handoffs"] >= 1  # emergency opens a handoff
    assert body["intent_breakdown"]["symptom_guidance"] == 1
    assert body["intent_breakdown"]["emergency_help"] == 1
    assert body["intent_breakdown"]["billing_query"] == 1


def test_stats_llm_assisted_zero_in_rule_based_mode(client):
    chat(client, "I have knee pain")
    body = client.get("/api/admin/stats").json()
    assert body["llm_assisted_responses"] == 0
