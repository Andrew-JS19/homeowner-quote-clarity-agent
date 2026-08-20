"""Small Cloud Run API for the bundled synthetic demonstration."""

from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException

from quote_clarity_agent.runtime import run_agent_review
from quote_clarity_agent.tools import FIXTURES
from src.quote_clarity import build_report


app = FastAPI(
    title="Homeowner Quote Clarity Agent",
    version="0.2.0",
    description="Synthetic evidence-first Google ADK demonstration.",
)
def _model_run_enabled() -> bool:
    return os.getenv("ENABLE_MODEL_RUN", "false").lower() == "true"


@app.get("/healthz")
async def healthz() -> dict[str, Any]:
    return {
        "status": "ok",
        "model": os.getenv("QUOTE_CLARITY_MODEL", "gemini-3.5-flash"),
        "cloud_project_configured": bool(os.getenv("GOOGLE_CLOUD_PROJECT")),
        "model_run_enabled": _model_run_enabled(),
        "input_policy": "bundled_synthetic_fixtures_only",
    }


@app.post("/v1/demo-runs")
async def run_demo() -> dict[str, Any]:
    """Run one bounded model-assisted review within the request lifecycle."""

    if not _model_run_enabled():
        raise HTTPException(status_code=503, detail="model_run_disabled")

    report = build_report(FIXTURES)
    try:
        review = await run_agent_review("bounded-synthetic-demo")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=type(exc).__name__) from exc

    return {
        "quote_count": len(report["quote_summaries"]),
        "missing_or_ambiguous_count": len(report["missing_and_ambiguities"]),
        "security_event_count": len(report["security_events"]),
        "decision_boundary": report["decision_boundary"],
        "agent_review": review,
    }
