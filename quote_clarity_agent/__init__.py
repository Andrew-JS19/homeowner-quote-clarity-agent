"""Google ADK entrypoint for Homeowner Quote Clarity Agent.

The bounded deterministic tools remain importable before optional ADK
dependencies are installed. Cloud and ADK entrypoints import ``agent``
directly once the declared requirements are present.
"""

try:
    from . import agent
except ModuleNotFoundError as exc:
    if exc.name not in {"google", "google.adk"}:
        raise
    agent = None

__all__ = ["agent"]
