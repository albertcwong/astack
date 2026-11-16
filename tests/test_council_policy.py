"""Check the council coordinator rules, not delegate execution."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CouncilPolicyTests(unittest.TestCase):
    def test_coordinator_triages_results_while_delegates_run(self):
        text = (ROOT / "skills" / "council" / "SKILL.md").read_text()
        for rule in (
            "Do not wait idle",
            "while the other delegates run",
            "Do not edit\nfiles while a delegate still reviews the same checkout",
            "non-blocking, do not wait for it",
            "do not record its score",
        ):
            self.assertIn(rule, text)
        self.assertNotIn("then `wait`", text)

    def test_default_members_are_claude_gpt_and_grok(self):
        text = (ROOT / "skills" / "council" / "SKILL.md").read_text()
        self.assertIn("latest flagship Claude Opus, GPT Sol, and Grok", text)
        self.assertIn("| Grok | 7/10 | 9/10 |", text)
        self.assertNotIn("Gemini Pro", text)


if __name__ == "__main__":
    unittest.main()
