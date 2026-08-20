import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from quote_clarity_agent.tools import (  # noqa: E402
    build_source_linked_demo_report,
    inspect_synthetic_fixture_manifest,
    verify_demo_safety_boundaries,
)


class AgentToolTests(unittest.TestCase):
    def test_manifest_is_bundled_and_synthetic(self):
        manifest = inspect_synthetic_fixture_manifest()
        self.assertEqual(manifest["fixture_count"], 4)
        self.assertFalse(manifest["external_sources"])
        self.assertTrue(
            all(item["classification"] == "fictional_synthetic_fixture" for item in manifest["fixtures"])
        )

    def test_report_tool_retains_non_decision_boundary(self):
        report = build_source_linked_demo_report()
        self.assertEqual(len(report["quote_summaries"]), 3)
        self.assertFalse(report["decision_boundary"]["performs_contractor_selection"])

    def test_safety_tool_passes_every_check(self):
        result = verify_demo_safety_boundaries()
        self.assertTrue(result["passed"])
        self.assertTrue(all(result["checks"].values()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
