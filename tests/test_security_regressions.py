"""Focused regressions for cryptographic integrity and input validation."""
import os

os.environ.setdefault("AUDIT_SECRET_KEY", "test-only-regression-signing-key-123456")
import pytest
from pydantic import ValidationError
from agents.base import AuditTrail
from agents.models import SystemTaskPayload
from agents.llm_factory import LLMFactory
from simulator import run_simulation


def test_audit_recomputes_signatures():
    ledger = AuditTrail(secret_key="unit-test-signing-key-1234567890")
    ledger.log("operator", "supervisor", "FIRST", {"task_id": "T1"})
    ledger.log("operator", "supervisor", "SECOND", {"task_id": "T2"})
    assert ledger.verify_integrity()
    ledger.logs[0]["event_type"] = "ALTERED"
    assert not ledger.verify_integrity()


def test_audit_detects_rehashed_but_unsigned_entry():
    ledger = AuditTrail(secret_key="unit-test-signing-key-1234567890")
    entry = ledger.log("operator", "supervisor", "FIRST", {"task_id": "T1"})
    ledger.logs[0]["payload_hash"] = "0" * 64
    assert not ledger.verify_integrity()
    assert entry["current_hash"] != "0" * 64


def test_audit_trail_is_defensive_copy():
    ledger = AuditTrail(secret_key="unit-test-signing-key-1234567890")
    ledger.log("operator", "supervisor", "FIRST", {"task_id": "T1"})
    snapshot = ledger.get_trail()
    snapshot[0]["actor"] = "tampered"
    snapshot.clear()
    assert ledger.verify_integrity()
    assert len(ledger.get_trail()) == 1


@pytest.mark.parametrize("value", [" ", "\t\n", "\x00\x07"])
def test_whitespace_and_control_only_identifiers_rejected(value):
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id=value, target_identifier="TARGET", primary_metric=1)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_metrics_rejected(value):
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="T1", target_identifier="TARGET", primary_metric=value)


def test_unimplemented_provider_does_not_silently_impersonate_llm():
    with pytest.raises(ValueError, match="Only the local deterministic mock"):
        LLMFactory.create("openai")


def test_zero_simulation_iterations_rejected():
    with pytest.raises(ValueError, match="positive"):
        run_simulation(0)
