"""Programmatic ADK runner used by the Cloud Run demonstration API."""

from __future__ import annotations

from google.adk.runners import InMemoryRunner
from google.genai import types

from .agent import root_agent


APP_NAME = "homeowner_quote_clarity"


async def run_agent_review(job_id: str) -> str:
    """Run one bounded ADK review and return only the final response text."""

    runner = InMemoryRunner(app_name=APP_NAME, agent=root_agent)
    user_id = "synthetic_demo"
    session = await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
    )
    message = types.Content(
        role="user",
        parts=[
            types.Part.from_text(
                text=(
                    f"Run synthetic quote-clarity job {job_id}. Use only bundled fixtures, "
                    "delegate all required checks, and return the bounded audit summary."
                )
            )
        ],
    )
    final_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message=message,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_text = "".join(part.text or "" for part in event.content.parts)
    if not final_text.strip():
        raise RuntimeError("agent_returned_no_final_text")
    return final_text.strip()
