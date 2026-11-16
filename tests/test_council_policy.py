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


if __name__ == "__main__":
    unittest.main()
