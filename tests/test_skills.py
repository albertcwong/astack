"""Check structure and the few rules whose loss would cause real harm.

These tests avoid pinning wording, so skills can be rewritten freely.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())
NAMES = {p.name for p in SKILLS}
RETIRED = {"full-stop", "modernize", "code-review-and-quality", "sol-loop"}


def text(name):
    return (ROOT / "skills" / name / "SKILL.md").read_text()


def frontmatter(body):
    match = re.match(r"---\n(.*?)\n---\n", body, re.S)
    return match.group(1) if match else ""


class SkillStructureTests(unittest.TestCase):
    def test_every_skill_has_matching_name_and_description(self):
        for skill in SKILLS:
            with self.subTest(skill=skill.name):
                meta = frontmatter(text(skill.name))
                self.assertRegex(meta, rf"(?m)^name: {re.escape(skill.name)}$")
                self.assertRegex(meta, r"(?m)^description: \S")

    def test_readme_table_lists_exactly_the_skills(self):
        readme = (ROOT / "README.md").read_text()
        listed = set(re.findall(r"(?m)^\| `([a-z0-9-]+)` \|", readme))
        self.assertEqual(listed, NAMES)

    def test_no_reference_to_a_retired_skill(self):
        files = [ROOT / "README.md", *(s / "SKILL.md" for s in SKILLS)]
        for path in files:
            for name in RETIRED:
                with self.subTest(file=path.name, skill=name):
                    self.assertNotIn(f"`{name}`", path.read_text())

    def test_readme_dependencies_name_real_skills(self):
        readme = (ROOT / "README.md").read_text()
        for line in re.findall(r"(?m)^- `[a-z-]+`.* uses? .*$", readme):
            for name in re.findall(r"`([a-z][a-z0-9-]+)`", line):
                if not name.startswith("verify-"):
                    with self.subTest(line=line, name=name):
                        self.assertIn(name, NAMES)


class SafetyRuleTests(unittest.TestCase):
    def test_full_stop_mode_never_merges(self):
        send = text("full-send")
        self.assertIn("full stop", frontmatter(send))
        self.assertIn("## Full stop mode", send)
        mode = send.split("## Full stop mode", 1)[1].split("\n## ", 1)[0]
        self.assertIn("Never merge it", mode)

    def test_pr_workflows_set_the_project_base(self):
        for name in ("full-send", "file-pr"):
            with self.subTest(skill=name):
                self.assertIn("--base <approved-target>", text(name))
        self.assertIn("wrong base blocks readiness and merging", text("babysit-pr"))
        self.assertIn("origin/<approved-target>", text("review-loop"))
        self.assertNotIn("origin/<default-branch>", text("review-loop"))

    def test_review_loop_routes_and_safety(self):
        review = text("review-loop")
        for route in ("| 1 | Sonnet | `claude`, `agent`, `pi` |",
                      "| 2 | Grok | `agent`, `pi` |",
                      "| 3 | Sol | `codex`, `agent`, `pi` |"):
            self.assertIn(route, review)
        for guard in ("--permission-mode plan", "--mode plan", "-s read-only",
                      "--tools read,grep,find,ls", "--session <session-file>",
                      "quota-limited", "never approval", "does not reset",
                      "only try routes that honor that choice",
                      "OpenCode is not a reviewer route"):
            self.assertIn(guard, review)
        self.assertIn("`review-loop`", text("full-send"))
        metadata = (ROOT / "skills/review-loop/agents/openai.yaml").read_text()
        self.assertIn("$review-loop", metadata)
        self.assertNotIn("sol-loop", metadata)

    def test_filing_a_pr_waits_for_required_checks(self):
        self.assertIn("pr-wait --until green", text("file-pr"))

    def test_review_handoff_is_on_request_and_generic(self):
        handoff = text("review-handoff")
        self.assertIn("only when the user asks", frontmatter(handoff))
        for project_specific in ("tableau", "tmtk", "/users/"):
            self.assertNotIn(project_specific, handoff.lower())


if __name__ == "__main__":
    unittest.main()
