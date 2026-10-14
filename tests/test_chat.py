"""Offline tests for the scoped chat guard (LLM is stubbed)."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from chat import Chat, OUT, REFUSE_AR, REFUSE_EN, compact_context  # noqa: E402

PLAN = json.loads((ROOT / "outputs" / "final_project_plan.json").read_text(encoding="utf-8"))


class Stub(Chat):
    def __init__(self, classifier="NO", answer="ok"):
        super().__init__(PLAN, "stub", "http://x")
        self.classifier, self.answer, self.calls = classifier, answer, []

    def _chat(self, messages, max_tokens, temperature=0.1):
        self.calls.append(max_tokens)
        return self.classifier if max_tokens == 3 else self.answer


class ChatGuardTests(unittest.TestCase):
    def test_context_is_compact(self):
        ctx = compact_context(PLAN)
        self.assertIn("TASK-027", ctx)
        self.assertLess(len(ctx), 9000)  # roughly < 3k tokens

    def test_ids_and_keywords_skip_classifier(self):
        b = Stub()
        self.assertEqual(b.ask("who owns TASK-007?"), "ok")
        self.assertEqual(b.ask("مين في الفريق على الباك اند"), "ok")
        self.assertEqual(b.calls, [400, 400])  # no classifier calls

    def test_offtopic_english_refused_by_classifier(self):
        b = Stub(classifier="NO")
        self.assertEqual(b.ask("how do I cook rice?"), REFUSE_EN)
        self.assertEqual(b.calls, [3])  # answer model never called

    def test_offtopic_arabic_refused(self):
        b = Stub(classifier="NO")
        self.assertEqual(b.ask("ازاي اعمل محشي؟"), REFUSE_AR)

    def test_unsure_classifier_refuses(self):
        self.assertEqual(Stub(classifier="maybe").ask("tell me a joke"), REFUSE_EN)

    def test_second_layer_catches_keyword_bait(self):
        b = Stub(answer=OUT)
        self.assertEqual(b.ask("which tasks should I cook for dinner?"), REFUSE_EN)

    def test_classifier_yes_allows_answer(self):
        self.assertEqual(Stub(classifier="YES").ask("is Docker ready by week four?"), "ok")

    def test_chinese_is_retried_then_clean(self):
        class Flaky(Stub):
            def _chat(self, messages, max_tokens, temperature=0.1):
                self.calls.append(max_tokens)
                return "Backend Developer 1 \u8fd9\u662f\u4e2d\u6587" if len(self.calls) == 1 else "Backend Developer 1: 6h"
        b = Flaky()
        self.assertEqual(b.ask("who owns TASK-007?"), "Backend Developer 1: 6h")
        self.assertEqual(len(b.calls), 2)

    def test_chinese_stripped_if_retry_still_dirty(self):
        b = Stub(answer="6h \u4e2d\u6587\u6d4b\u8bd5 done")
        self.assertEqual(b.ask("who owns TASK-007?"), "6h done")


if __name__ == "__main__":
    unittest.main()
