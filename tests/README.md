# CarePath AI — Tests

A `pytest` suite covering the backend end-to-end. All tests run **offline in
deterministic rule-based mode** (the LLM is force-disabled in `conftest.py`), so
they're fast, hermetic, and don't need an `ANTHROPIC_API_KEY`.

## Install

```bash
.venv\Scripts\activate            # Windows
pip install -r requirements-dev.txt
```

## Run

```bash
pytest                     # everything (151 tests)
pytest -m unit             # fast, isolated module tests
pytest -m integration      # full app via FastAPI TestClient
pytest tests/test_safety.py -v   # one file, verbose
pytest -k emergency        # tests matching a keyword
```

## Layout

| File                     | Scope        | What it covers |
| ------------------------ | ------------ | -------------- |
| `test_safety.py`         | unit         | Emergency red-flag + distress detection, disclaimers |
| `test_intent.py`         | unit         | Keyword intent detection + precedence quirks |
| `test_journey.py`        | unit         | Intent→stage mapping, next-best-action |
| `test_mock_data.py`      | unit         | Department/doctor lookups + data integrity |
| `test_store.py`          | unit         | Sessions, appointment IDs, audit, masked handoffs |
| `test_llm.py`            | unit         | Fault-tolerant LLM wrapper (never raises, returns None) |
| `test_agents.py`         | unit         | Each specialized agent's deterministic path |
| `test_chat_api.py`       | integration  | `POST /api/chat` orchestration flows |
| `test_reference_api.py`  | integration  | Health, doctors, departments, sessions |
| `test_admin_api.py`      | integration  | Handoff queue, audit log, stats |

## Notes

- `conftest.py` provides two autouse fixtures: `force_rule_based` (deterministic
  output) and `reset_state` (clears the shared in-memory store between tests).
- To exercise the **LLM path** instead, you'd set `ANTHROPIC_API_KEY` and remove
  the `force_rule_based` fixture — but those calls are non-deterministic and cost
  money, so they're intentionally excluded from this suite.
