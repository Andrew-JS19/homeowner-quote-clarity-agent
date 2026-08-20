"""Bounded tools exposed to the Google ADK agents.

Every tool operates only on the bundled fictional fixtures. No tool can browse,
send a message, execute an attachment, or change an external system.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from src.quote_clarity import build_report


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"


def inspect_synthetic_fixture_manifest() -> dict[str, Any]:
    """Return filenames, byte sizes, and hashes for bundled fictional fixtures."""

    items = []
    for path in sorted(FIXTURES.glob("*.txt")):
        payload = path.read_bytes()
        items.append(
            {
                "filename": path.name,
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "classification": "fictional_synthetic_fixture",
            }
        )
    return {"fixture_count": len(items), "fixtures": items, "external_sources": False}


def build_source_linked_demo_report() -> dict[str, Any]:
    """Build the deterministic source-linked comparison for bundled fixtures."""

    return build_report(FIXTURES)


def verify_demo_safety_boundaries() -> dict[str, Any]:
    """Rebuild and validate non-decision, evidence, and injection safeguards."""

    report = build_report(FIXTURES)
    boundary = report["decision_boundary"]
    all_summaries_have_evidence = all(
        summary.get("total_evidence") is not None for summary in report["quote_summaries"]
    )
    checks = {
        "three_quotes_processed": len(report["quote_summaries"]) == 3,
        "source_evidence_present": all_summaries_have_evidence,
        "injection_quarantined": any(
            item.get("event") == "prompt_injection_quarantined"
            for item in report["security_events"]
        ),
        "no_contractor_selection": boundary["performs_contractor_selection"] is False,
        "no_fairness_assessment": boundary["performs_price_fairness_assessment"] is False,
        "no_external_actions": boundary["performs_external_actions"] is False,
    }
    return {"passed": all(checks.values()), "checks": checks}
