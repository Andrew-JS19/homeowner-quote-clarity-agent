"""Deterministic offline vertical slice for synthetic quote comparison.

This module deliberately uses no network, model, API, cloud, or external package.
It simulates the structured evidence contract planned for a future ADK/Gemini build.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


PROJECT = "Pinehaven Cottage Bathroom Refresh - Synthetic Demonstration"
FIXED_PACKAGE_DATE = "2026-08-20"

REQUIRED_SCOPE = (
    "demolition",
    "waste",
    "waterproofing",
    "tiling",
    "plumbing",
    "electrical",
    "sanitaryware",
    "painting",
)

SCOPE_ALIASES = {
    "demolition": "demolition",
    "demolition works": "demolition",
    "strip-out and demolition": "demolition",
    "waste removal": "waste",
    "rubble disposal": "waste",
    "waterproofing": "waterproofing",
    "waterproof membrane": "waterproofing",
    "waterproofing system": "waterproofing",
    "wall and floor tiling": "tiling",
    "tiling": "tiling",
    "wall/floor tile installation": "tiling",
    "plumbing alterations": "plumbing",
    "plumbing": "plumbing",
    "plumbing changes": "plumbing",
    "electrical alterations": "electrical",
    "electrical": "electrical",
    "electrical changes": "electrical",
    "sanitaryware": "sanitaryware",
    "fittings and sanitaryware": "sanitaryware",
    "sanitary fittings": "sanitaryware",
    "painting and finishing": "painting",
    "paint and final finish": "painting",
    "painting": "painting",
}

ALLOWED_RECORDS = {"META", "TOTAL", "SCOPE", "TERM"}
ALLOWED_COMMERCIAL_TYPES = {"fixed", "allowance", "provisional", "optional", "excluded", "unknown"}
INJECTION_PATTERNS = (
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"mark\s+.+\s+as\s+the\s+winner", re.IGNORECASE),
    re.compile(r"omit\s+the\s+payment", re.IGNORECASE),
)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _evidence(path: Path, line_number: int, raw_line: str) -> Dict[str, Any]:
    return {
        "source_file": path.name,
        "source_line": line_number,
        "source_excerpt_hash": _sha256_text(raw_line),
    }


def _parse_amount(raw: str) -> Dict[str, Any]:
    if raw == "UNKNOWN":
        return {"value": None, "confidence": "medium", "verification_state": "needs-human-review"}

    corrected = raw
    ocr_ambiguous = bool(re.search(r"[Oo]", raw))
    if ocr_ambiguous:
        corrected = re.sub(r"[Oo]", "0", raw)
    digits = re.sub(r"[^0-9]", "", corrected)
    if not digits:
        return {"value": None, "confidence": "low", "verification_state": "needs-human-review"}
    return {
        "value": int(digits),
        "confidence": "low" if ocr_ambiguous else "high",
        "verification_state": "needs-human-review" if ocr_ambiguous else "extracted",
    }


def _is_injection(text: str) -> bool:
    return any(pattern.search(text) for pattern in INJECTION_PATTERNS)


def parse_quote_fixture(path: Path) -> Dict[str, Any]:
    """Parse the controlled synthetic text-fixture format."""

    meta: Dict[str, str] = {}
    facts: List[Dict[str, Any]] = []
    security_events: List[Dict[str, Any]] = []

    lines = path.read_text(encoding="utf-8").splitlines()
    for number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if _is_injection(line):
            security_events.append(
                {
                    "event": "prompt_injection_quarantined",
                    "source_file": path.name,
                    "source_line": number,
                    "source_excerpt_hash": _sha256_text(raw_line),
                    "action": "ignored_as_instruction",
                }
            )
            continue

        parts = line.split("|")
        record = parts[0]
        if record not in ALLOWED_RECORDS:
            security_events.append(
                {
                    "event": "unsupported_record_quarantined",
                    "source_file": path.name,
                    "source_line": number,
                    "source_excerpt_hash": _sha256_text(raw_line),
                    "action": "not_added_to_evidence",
                }
            )
            continue

        evidence = _evidence(path, number, raw_line)
        if record == "META" and len(parts) == 3:
            meta[parts[1]] = parts[2]
        elif record == "TOTAL" and len(parts) == 3:
            amount = _parse_amount(parts[1])
            facts.append(
                {
                    "kind": "total",
                    "key": "quoted_total",
                    "original_label": "TOTAL",
                    "normalized_category": "quoted_total",
                    "raw_value": parts[1],
                    "value": amount["value"],
                    "currency": "ZAR",
                    "tax_basis": parts[2],
                    "commercial_type": "fixed",
                    "confidence": amount["confidence"],
                    "verification_state": amount["verification_state"],
                    "notes": "OCR ambiguity detected" if amount["confidence"] == "low" else "",
                    "evidence": evidence,
                }
            )
        elif record == "SCOPE" and len(parts) == 5:
            original = parts[1]
            normalized = SCOPE_ALIASES.get(original.lower(), "unknown")
            commercial_type = parts[3]
            if commercial_type not in ALLOWED_COMMERCIAL_TYPES:
                raise ValueError(f"Unsupported commercial type {commercial_type!r} in {path.name}:{number}")
            amount = _parse_amount(parts[2])
            facts.append(
                {
                    "kind": "scope",
                    "key": normalized,
                    "original_label": original,
                    "normalized_category": normalized,
                    "raw_value": parts[2],
                    "value": amount["value"],
                    "currency": "ZAR",
                    "tax_basis": "per_quote",
                    "commercial_type": commercial_type,
                    "confidence": "low" if normalized == "unknown" else amount["confidence"],
                    "verification_state": "needs-human-review" if normalized == "unknown" else amount["verification_state"],
                    "notes": parts[4],
                    "evidence": evidence,
                }
            )
        elif record == "TERM" and len(parts) == 3:
            value: Optional[str] = None if parts[2] == "UNKNOWN" else parts[2]
            facts.append(
                {
                    "kind": "term",
                    "key": parts[1],
                    "original_label": parts[1],
                    "normalized_category": parts[1],
                    "raw_value": parts[2],
                    "value": value,
                    "currency": None,
                    "tax_basis": None,
                    "commercial_type": "unknown" if value is None else "fixed",
                    "confidence": "medium" if value is None else "high",
                    "verification_state": "needs-human-review" if value is None else "extracted",
                    "notes": "Not stated" if value is None else "",
                    "evidence": evidence,
                }
            )
        else:
            raise ValueError(f"Malformed record in {path.name}:{number}: {raw_line}")

    if "quote_id" not in meta or "contractor" not in meta:
        raise ValueError(f"Quote metadata missing in {path.name}")

    return {"meta": meta, "facts": facts, "security_events": security_events}


def parse_attachment(path: Path) -> Dict[str, Any]:
    """Quarantine unsupported instructions; no attachment content becomes a quote fact."""

    security_events: List[Dict[str, Any]] = []
    associated_quote: Optional[str] = None
    for number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("|", 2)
        if parts[0] == "META" and len(parts) == 3 and parts[1] == "associated_quote":
            associated_quote = parts[2]
            continue
        event = "prompt_injection_quarantined" if _is_injection(line) or parts[0] == "INSTRUCTION" else "unsupported_record_quarantined"
        security_events.append(
            {
                "event": event,
                "source_file": path.name,
                "source_line": number,
                "source_excerpt_hash": _sha256_text(raw_line),
                "action": "ignored_as_instruction" if event == "prompt_injection_quarantined" else "not_added_to_evidence",
                "associated_quote": associated_quote,
            }
        )
    return {"associated_quote": associated_quote, "facts": [], "security_events": security_events}


def _fact_by_key(quote: Dict[str, Any], key: str, kind: Optional[str] = None) -> Optional[Dict[str, Any]]:
    for fact in quote["facts"]:
        if fact["key"] == key and (kind is None or fact["kind"] == kind):
            return fact
    return None


def _missing_items(quote: Dict[str, Any]) -> List[Dict[str, Any]]:
    quote_id = quote["meta"]["quote_id"]
    missing: List[Dict[str, Any]] = []
    available_scope = {fact["key"] for fact in quote["facts"] if fact["kind"] == "scope"}
    for category in REQUIRED_SCOPE:
        if category not in available_scope:
            missing.append(
                {
                    "quote_id": quote_id,
                    "field": category,
                    "state": "unknown",
                    "reason": "not_stated",
                    "question": f"Please confirm whether {category} is included, excluded, optional, or owner-supplied.",
                }
            )

    for required_term in ("validity", "electrical_handover"):
        fact = _fact_by_key(quote, required_term, "term")
        if fact is None or fact["value"] is None:
            missing.append(
                {
                    "quote_id": quote_id,
                    "field": required_term,
                    "state": "unknown",
                    "reason": "not_stated",
                    "question": (
                        "Please state the quotation validity period."
                        if required_term == "validity"
                        else "Please confirm what electrical testing or handover record is included, if any."
                    ),
                }
            )
    return missing


def build_report(fixtures_dir: Path) -> Dict[str, Any]:
    quote_paths = sorted(path for path in fixtures_dir.glob("*.txt") if path.name != "contractor_notes_and_scope.txt")
    quotes = [parse_quote_fixture(path) for path in quote_paths]
    quotes.sort(key=lambda item: item["meta"]["quote_id"])

    attachment = parse_attachment(fixtures_dir / "contractor_notes_and_scope.txt")
    security_events = [event for quote in quotes for event in quote["security_events"]] + attachment["security_events"]

    comparison: List[Dict[str, Any]] = []
    for category in REQUIRED_SCOPE:
        row: Dict[str, Any] = {"category": category, "quotes": {}}
        for quote in quotes:
            quote_id = quote["meta"]["quote_id"]
            fact = _fact_by_key(quote, category, "scope")
            row["quotes"][quote_id] = (
                {
                    "state": "stated",
                    "amount": fact["value"],
                    "commercial_type": fact["commercial_type"],
                    "original_label": fact["original_label"],
                    "notes": fact["notes"],
                    "evidence": fact["evidence"],
                }
                if fact
                else {"state": "unknown", "amount": None, "commercial_type": "unknown", "evidence": None}
            )
        comparison.append(row)

    quote_summaries: List[Dict[str, Any]] = []
    missing: List[Dict[str, Any]] = []
    for quote in quotes:
        total = _fact_by_key(quote, "quoted_total", "total")
        terms = {fact["key"]: {"value": fact["value"], "evidence": fact["evidence"]} for fact in quote["facts"] if fact["kind"] == "term"}
        quote_missing = _missing_items(quote)
        missing.extend(quote_missing)
        quote_summaries.append(
            {
                "quote_id": quote["meta"]["quote_id"],
                "contractor": quote["meta"]["contractor"],
                "quoted_total": total["value"],
                "total_raw": total["raw_value"],
                "currency": total["currency"],
                "tax_basis": total["tax_basis"],
                "total_confidence": total["confidence"],
                "total_verification_state": total["verification_state"],
                "total_evidence": total["evidence"],
                "terms": terms,
                "neutral_questions": [item["question"] for item in quote_missing],
            }
        )

    return {
        "schema_version": "0.1.0-offline-simulation",
        "package_date": FIXED_PACKAGE_DATE,
        "project": PROJECT,
        "input_classification": "entirely_fictional_synthetic_fixtures",
        "processing_mode": "deterministic_rules_simulation_no_model_no_network",
        "quote_summaries": quote_summaries,
        "scope_comparison": comparison,
        "missing_and_ambiguities": missing,
        "security_events": security_events,
        "decision_boundary": {
            "performs_contractor_selection": False,
            "performs_price_fairness_assessment": False,
            "performs_legal_or_technical_compliance_assessment": False,
            "performs_external_actions": False,
            "statement": "This report organizes stated evidence and neutral questions. A homeowner and qualified advisers make all decisions.",
        },
        "simulation_notice": (
            "Text extraction, agent delegation, Gemini reasoning, Google ADK orchestration, asynchronous Cloud Run execution, "
            "Firestore state, production security, and model evaluation are not implemented in this offline vertical slice."
        ),
    }


def render_markdown(report: Dict[str, Any]) -> str:
    lines = [
        "# Homeowner Quote Clarity Report - Synthetic Offline Demonstration",
        "",
        f"**Project:** {report['project']}  ",
        f"**Mode:** {report['processing_mode']}  ",
        "",
        "> This report organizes fictional stated evidence. It does not select a contractor or assess fairness, safety, legality, or technical sufficiency.",
        "",
        "## Quote summary",
        "",
        "| Quote | Contractor | Stated total | Tax basis | Confidence |",
        "|---|---|---:|---|---|",
    ]
    for quote in report["quote_summaries"]:
        amount = f"ZAR {quote['quoted_total']:,}" if quote["quoted_total"] is not None else "Unknown"
        lines.append(f"| {quote['quote_id']} | {quote['contractor']} | {amount} | {quote['tax_basis']} | {quote['total_confidence']} |")

    lines.extend(["", "Totals are not normalized or ranked. Quote B excludes VAT and contains an OCR-ambiguous total that requires human review.", "", "## Scope comparison", ""])
    header = "| Category | " + " | ".join(q["quote_id"] for q in report["quote_summaries"]) + " |"
    lines.append(header)
    lines.append("|---|" + "---|" * len(report["quote_summaries"]))
    for row in report["scope_comparison"]:
        cells = []
        for quote in report["quote_summaries"]:
            cell = row["quotes"][quote["quote_id"]]
            if cell["state"] == "unknown":
                cells.append("Unknown / not stated")
            else:
                amount = f"ZAR {cell['amount']:,}" if cell["amount"] is not None else "No separate amount"
                cells.append(f"{cell['commercial_type']}; {amount}")
        lines.append("| " + row["category"] + " | " + " | ".join(cells) + " |")

    lines.extend(["", "## Missing information and neutral questions", ""])
    for quote in report["quote_summaries"]:
        lines.append(f"### Quote {quote['quote_id']}")
        lines.extend(f"- {question}" for question in quote["neutral_questions"])
        if not quote["neutral_questions"]:
            lines.append("- No required-field omissions detected by this fixture schema.")
        lines.append("")

    lines.extend(
        [
            "## Security and evidence",
            "",
            f"- Quarantined attachment records: {len(report['security_events'])}",
            "- Raw adversarial instructions are not reproduced in the report.",
            "- Every stated amount and term retains a source file, line and SHA-256 excerpt hash in the JSON report.",
            "",
            "## Decision boundary",
            "",
            report["decision_boundary"]["statement"],
            "",
            "## Simulation notice",
            "",
            report["simulation_notice"],
            "",
        ]
    )
    return "\n".join(lines)


def canonical_json(report: Dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
