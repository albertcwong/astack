"""Check the documented handoff contract, not agent execution or server behavior."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ReviewHandoffPolicyTests(unittest.TestCase):
    def skill(self, name):
        return (ROOT / "skills" / name / "SKILL.md").read_text()

    def test_both_delivery_skills_require_shared_protocol(self):
        for name in ("full-send", "full-stop"):
            with self.subTest(skill=name):
                text = self.skill(name)
                self.assertIn("../review-handoff/SKILL.md", text)
                self.assertIn("at work start", text)
                self.assertIn("handoff", text)
        send = self.skill("full-send")
        self.assertIn("before merge", send)
        self.assertIn("all project-required human acceptance", send)
        self.assertIn("approved local task", send)
        stop = self.skill("full-stop")
        self.assertIn("Never merge it", stop)
        self.assertIn("A stopped server is not ready", stop)

    def test_identity_recovery_and_truthful_states(self):
        text = self.skill("review-handoff")
        for requirement in (
            "full issue URL or tracker-qualified identifier",
            "approved local task identifier",
            "existing work item",
            "base SHA",
            "Full committed candidate SHA",
            "Read the record back",
            "actual process state",
            "Registered:",
            "Stopped:",
            "Superseded:",
            "Not applicable:",
            "restart and stop commands",
            "not an installed",
            "perform\nand record these checks manually",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, text)

    def test_runtime_safety_and_project_independence(self):
        text = self.skill("review-handoff")
        for requirement in (
            "pinned to the",
            "uncommitted changes",
            "actual bind succeeds",
            "Never kill an",
            "loopback",
            "PID plus start",
            "Do not inherit live credentials",
            "matching built assets",
            "Do not promise",
            "publish only approved sanitized evidence",
        ):
            self.assertIn(requirement, text)
        for project_specific in (
            "tableau",
            "tmtk",
            "tasks.json",
            "control.transaction",
            "18880",
            "/Users/albert",
            "workspace/local-agents",
        ):
            self.assertNotIn(project_specific, text)

    def test_readme_lists_protocol(self):
        text = (ROOT / "README.md").read_text()
        self.assertIn("| `review-handoff` |", text)
        self.assertIn("not a server launcher or automatic status validator", text)


if __name__ == "__main__":
    unittest.main()
