import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    from google.adk.runners import InMemoryRunner
    from quote_clarity_agent.agent import root_agent
    from quote_clarity_agent.runtime import APP_NAME
except ModuleNotFoundError:
    InMemoryRunner = None


@unittest.skipIf(InMemoryRunner is None, "Google ADK dependencies are not installed")
class AdkSmokeTests(unittest.IsolatedAsyncioTestCase):
    async def test_agent_tree_and_session_initialize_without_model_call(self):
        self.assertEqual(root_agent.name, "quote_clarity_coordinator")
        self.assertEqual(
            [agent.name for agent in root_agent.sub_agents],
            ["manifest_agent", "evidence_agent", "safety_agent"],
        )
        runner = InMemoryRunner(app_name=APP_NAME, agent=root_agent)
        session = await runner.session_service.create_session(
            app_name=APP_NAME,
            user_id="smoke_test",
        )
        self.assertTrue(session.id)


if __name__ == "__main__":
    unittest.main(verbosity=2)
