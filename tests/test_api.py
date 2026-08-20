import os
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import app  # noqa: E402


class ApiTests(unittest.IsolatedAsyncioTestCase):
    async def test_health_reports_fail_closed_defaults(self):
        with patch.dict(os.environ, {}, clear=True):
            response = await app.healthz()
        self.assertEqual(response["status"], "ok")
        self.assertFalse(response["cloud_project_configured"])
        self.assertFalse(response["model_run_enabled"])
        self.assertEqual(response["input_policy"], "bundled_synthetic_fixtures_only")

    async def test_demo_run_is_disabled_by_default(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(HTTPException) as caught:
                await app.run_demo()
        self.assertEqual(caught.exception.status_code, 503)
        self.assertEqual(caught.exception.detail, "model_run_disabled")

    async def test_enabled_demo_returns_bounded_summary(self):
        with (
            patch.dict(os.environ, {"ENABLE_MODEL_RUN": "true"}, clear=True),
            patch.object(
                app,
                "run_agent_review",
                new=AsyncMock(return_value="Synthetic review completed; no contractor selected."),
            ),
        ):
            response = await app.run_demo()
        self.assertEqual(response["quote_count"], 3)
        self.assertFalse(response["decision_boundary"]["performs_contractor_selection"])
        self.assertIn("no contractor selected", response["agent_review"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
