"""
Automated Pytest for rowhammer-dram-mitigation-agent Enrichment Modules.
"""
import os
import sys
from pathlib import Path

# Set audit secret key before importing agents
os.environ.setdefault("AUDIT_SECRET_KEY", "test-audit-secret-key-2026-minimum-16-chars")

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from enrichment import (
    FeaturesEngine,
    RowhammerBitFlipDetectionAndCharacterizationEngine,
    TrrTargetRowRefreshEffectivenessTestingEngine,
    RowhammerForPrivilegeEscalationEngine,
    EccDramRowhammerResistanceEvaluationEngine,
    RowhammerMitigationOverheadMeasurementEngine,
    RowhammerForColdBootAttackEnhancementEngine,
    DramAgingAndRowhammerCorrelationEngine,
    RowhammerdrammitigationagentEnrichmentSuite,
    enrichment_suite,
)

def test_enrichment_suite_execution():
    suite = RowhammerdrammitigationagentEnrichmentSuite()
    res = suite.execute_all(primary_val=0.5, secondary_val=0.2)
    assert len(res) >= 1
    for k, v in res.items():
        assert v.status in ["OPTIMAL", "WARNING", "CRITICAL_ALERT"]
        assert isinstance(v.recommendations, list)

def test_enrichment_threshold_escalation():
    suite = RowhammerdrammitigationagentEnrichmentSuite()
    res = suite.execute_all(primary_val=10.0, secondary_val=5.0)
    for k, v in res.items():
        assert v.status in ["WARNING", "CRITICAL_ALERT"]
        assert len(v.alerts) > 0
