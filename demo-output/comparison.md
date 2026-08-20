# Homeowner Quote Clarity Report - Synthetic Offline Demonstration

**Project:** Pinehaven Cottage Bathroom Refresh - Synthetic Demonstration
**Mode:** deterministic_rules_simulation_no_model_no_network

> This report organizes fictional stated evidence. It does not select a contractor or assess fairness, safety, legality, or technical sufficiency.

## Quote summary

| Quote | Contractor | Stated total | Tax basis | Confidence |
|---|---|---:|---|---|
| A | SampleBuild Alpha (fictional) | ZAR 84,500 | VAT_INCLUDED | high |
| B | SampleBuild Beta (fictional) | ZAR 78,900 | VAT_EXCLUDED | low |
| C | SampleBuild Gamma (fictional) | ZAR 92,300 | VAT_INCLUDED | high |

Totals are not normalized or ranked. Quote B excludes VAT and contains an OCR-ambiguous total that requires human review.

## Scope comparison

| Category | A | B | C |
|---|---|---|---|
| demolition | fixed; ZAR 12,000 | fixed; ZAR 9,000 | fixed; ZAR 11,000 |
| waste | fixed; ZAR 4,500 | Unknown / not stated | fixed; ZAR 5,000 |
| waterproofing | fixed; ZAR 16,000 | fixed; ZAR 14,000 | fixed; ZAR 17,000 |
| tiling | fixed; ZAR 29,000 | allowance; ZAR 12,000 | fixed; ZAR 26,000 |
| plumbing | fixed; ZAR 14,000 | fixed; ZAR 13,000 | fixed; ZAR 15,000 |
| electrical | fixed; ZAR 9,000 | fixed; ZAR 8,000 | optional; ZAR 3,500 |
| sanitaryware | excluded; No separate amount | excluded; No separate amount | allowance; ZAR 15,000 |
| painting | fixed; No separate amount | fixed; ZAR 5,000 | fixed; ZAR 6,500 |

## Missing information and neutral questions

### Quote A
- Please state the quotation validity period.
- Please confirm what electrical testing or handover record is included, if any.

### Quote B
- Please confirm whether waste is included, excluded, optional, or owner-supplied.
- Please confirm what electrical testing or handover record is included, if any.

### Quote C
- Please confirm what electrical testing or handover record is included, if any.

## Security and evidence

- Quarantined attachment records: 2
- Raw adversarial instructions are not reproduced in the report.
- Every stated amount and term retains a source file, line and SHA-256 excerpt hash in the JSON report.

## Decision boundary

This report organizes stated evidence and neutral questions. A homeowner and qualified advisers make all decisions.

## Simulation notice

Text extraction, live agent delegation, Gemini reasoning, live Google ADK orchestration, Cloud Run execution, production security, and model evaluation are not implemented in this offline vertical slice. ADK agent definitions and local in-memory session initialization are tested separately without a model call.
