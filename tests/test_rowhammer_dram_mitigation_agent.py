"""
Automated Pytest Test Suite for Rowhammer Dram Mitigation Agent.
Domain: Clinical & Biomedical AI
Standard: CAP / CLSI / ISO Standards
"""
import os
import sys
from pathlib import Path

# Set audit secret key before importing agents
os.environ.setdefault("AUDIT_SECRET_KEY", "test-audit-secret-key-2026-minimum-16-chars")

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, SecurityException
from agents.models import SystemTaskPayload, UrgencyLevel, SystemIntegrityStatus
from agents.workers import InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker
from agents.supervisor import SystemSupervisor
from cli import main


def test_phi_guard_enforcement():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive for Staphylococcus")

    # Clean text passes
    PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")


def test_specialized_workers():
    # Worker 1: QC Invariant
    p1 = SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=35.0)
    alerts1 = InvariantQCWorker.evaluate(p1)
    assert len(alerts1) == 1
    assert alerts1[0].urgency == UrgencyLevel.ELEVATED

    # Worker 2: Safety
    p2 = SystemTaskPayload(task_id="T2", target_identifier="KEY-02", primary_metric=10.0, is_critical_flag=True)
    alerts2 = SafetyEscalationWorker.evaluate(p2)
    assert len(alerts2) == 1
    assert alerts2[0].urgency == UrgencyLevel.CRITICAL_STAT

    # Worker 3: Protocol Conformance
    p3 = SystemTaskPayload(task_id="T3", target_identifier="KEY-03", primary_metric=10.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = ProtocolConformanceWorker.evaluate(p3)
    assert len(alerts3) == 1


def test_supervisor_consensus_and_audit():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TASK-PROD-01",
        target_identifier="KEY-PROD-01",
        primary_metric=12.0,
        secondary_metric=4.0,
        status_descriptor="NOMINAL"
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.ROUTINE
    assert dossier.integrity_status == SystemIntegrityStatus.VALIDATED
    assert dossier.audit_hash != ""

    # Verify cryptographic audit trail
    assert AuditLogger.verify_integrity() is True

    # CLI tests
    assert main(["audit", "--task-id", "CLI-TEST-01"]) == 0
    assert main(["chat", "Explain", "specifications"]) == 0
    assert main(["verify-audit"]) == 0


def test_audit_trail_requires_secret_key():
    """AuditTrail must reject empty/short secret keys."""
    from agents.base import AuditTrail
    import os

    # Save and clear env var
    saved = os.environ.pop("AUDIT_SECRET_KEY", None)
    try:
        # Empty key should raise SecurityException
        with pytest.raises(Exception):
            AuditTrail(secret_key="")
        # Short key should raise SecurityException
        with pytest.raises(Exception):
            AuditTrail(secret_key="short")
        # Valid key should work
        trail = AuditTrail(secret_key="valid-test-key-1234567890")
        assert trail is not None
    finally:
        # Restore env var
        if saved:
            os.environ["AUDIT_SECRET_KEY"] = saved


def test_phi_guard_redaction():
    """PHIGuard should redact sensitive patterns."""
    redacted = PHIGuard.redact_phi("Contact patient at 555-123-4567 or MRN-12345")
    assert "555-123-4567" not in redacted
    assert "MRN-12345" not in redacted
    assert "REDACTED" in redacted


def test_input_validation_bounds():
    """SystemTaskPayload should reject out-of-bounds metrics."""
    import pytest
    from pydantic import ValidationError

    # Valid payload
    p = SystemTaskPayload(task_id="T1", target_identifier="K1", primary_metric=50.0)
    assert p.primary_metric == 50.0

    # Out-of-bounds should fail
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="T1", target_identifier="K1", primary_metric=9999.0)

    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="T1", target_identifier="K1", primary_metric=-9999.0)

    # Empty task_id should fail
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="", target_identifier="K1", primary_metric=10.0)


def test_batch_file_not_found():
    """CLI batch command should handle missing files gracefully."""
    result = main(["batch", "-i", "nonexistent_file.csv"])
    assert result == 1
