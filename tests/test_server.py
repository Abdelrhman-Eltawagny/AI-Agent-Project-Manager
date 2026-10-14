"""Offline tests for the web API (LLM stubbed)."""
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ["PLAN_PATH"] = str(ROOT / "outputs" / "final_project_plan.json")
os.environ["API_KEY"] = "secret"

from fastapi.testclient import TestClient  # noqa: E402

import chat  # noqa: E402
import server  # noqa: E402


def fake(self, messages, max_tokens, temperature=0.1):
    return "NO" if max_tokens == 3 else "Backend Developer 1: 6h"


class ServerTests(unittest.TestCase):
    def setUp(self):
        chat.Chat._chat = fake
        server._sessions.clear()
        self.c = TestClient(server.app)

    def test_health_and_page(self):
        self.assertEqual(self.c.get("/health").json()["status"], "ok")
        self.assertIn("Project Assistant", self.c.get("/").text)

    def test_requires_api_key(self):
        r = self.c.post("/ask", json={"question": "who owns TASK-007?"})
        self.assertEqual(r.status_code, 401)

    def test_answers_and_refuses(self):
        h = {"x-api-key": "secret"}
        r = self.c.post("/ask", json={"question": "who owns TASK-007?", "session_id": "a"}, headers=h)
        self.assertEqual(r.json()["answer"], "Backend Developer 1: 6h")
        r = self.c.post("/ask", json={"question": "how do I cook rice?", "session_id": "a"}, headers=h)
        self.assertIn("only answer questions about this project", r.json()["answer"])

    def test_empty_question_rejected(self):
        r = self.c.post("/ask", json={"question": ""}, headers={"x-api-key": "secret"})
        self.assertEqual(r.status_code, 422)


if __name__ == "__main__":
    unittest.main()
