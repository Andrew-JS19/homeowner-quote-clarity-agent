from pathlib import Path

from src.quote_clarity import build_report, canonical_json, render_markdown


def main() -> None:
    root = Path(__file__).resolve().parent
    output = root / "demo-output"
    output.mkdir(exist_ok=True)
    report = build_report(root / "fixtures")
    (output / "report.json").write_text(canonical_json(report), encoding="utf-8")
    (output / "comparison.md").write_text(render_markdown(report), encoding="utf-8")
    print(
        "Built deterministic synthetic report: "
        f"{len(report['quote_summaries'])} quotes, "
        f"{len(report['missing_and_ambiguities'])} missing/ambiguous fields, "
        f"{len(report['security_events'])} quarantined attachment records."
    )


if __name__ == "__main__":
    main()
