"""Guard against restoring default-branch assumptions in PR workflows."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PrTargetPolicyTests(unittest.TestCase):
    def skill(self, name):
        return (ROOT / "skills" / name / "SKILL.md").read_text()

    def test_send_resolves_and_checks_project_target(self):
        text = self.skill("full-send")
        for rule in (
            "CONTRIBUTING.md", "--base <approved-target>",
            "baseRefName, headRefName and headRefOid",
            "Full-send does not authorize a release",
            "immediately before merge", "Never bypass protection",
        ):
            self.assertIn(rule, text)
        self.assertNotIn("Rebase onto the latest default", text)
        self.assertNotIn("up to date with the default branch", text)

    def test_stop_checks_target_without_merge_permission(self):
        text = self.skill("full-stop")
        for rule in (
            "CONTRIBUTING.md", "Set the base explicitly", "before each push",
            "Never declare a wrongly targeted PR ready", "Never merge it",
            "Never merge, enable auto-merge, enter a merge queue",
            "including for a correctly targeted and fully approved release PR",
        ):
            self.assertIn(rule, text)

    def test_delegated_skills_do_not_redirect_to_main(self):
        filing = self.skill("file-pr")
        watching = self.skill("babysit-pr")
        self.assertIn("--base <approved-target>", filing)
        self.assertIn("CONTRIBUTING.md", filing)
        self.assertNotIn("usually `origin/main`", filing)
        self.assertIn("wrong base blocks readiness and merging", watching)
        self.assertNotIn("Keep an eye on changes to `main`", watching)


if __name__ == "__main__":
    unittest.main()
