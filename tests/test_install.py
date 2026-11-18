"""scripts/install links skills, keeps backups, and leaves other skills alone."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "install"


def make_skill(folder, name):
    (folder / name).mkdir(parents=True)
    (folder / name / "SKILL.md").write_text(f"---\nname: {name}\n---\n")


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def run_install(self, *arguments):
        return subprocess.run([sys.executable, str(SCRIPT), "--home", str(self.home), *arguments],
                              check=True, capture_output=True, text=True).stdout

    def test_links_every_skill_into_both_folders(self):
        self.run_install()
        for folder in (".claude/skills", ".agents/skills"):
            link = self.home / folder / "full-send"
            self.assertTrue(link.is_symlink())
            self.assertEqual(link.resolve(), (ROOT / "skills" / "full-send").resolve())
        self.assertEqual(self.run_install().strip(), "Nothing to change.")

    def test_backs_up_old_copies_and_keeps_other_skills(self):
        claude = self.home / ".claude/skills"
        make_skill(claude, "full-send")
        make_skill(claude, "full-stop")
        make_skill(claude, "query-tableau-data")
        self.run_install()
        self.assertTrue((claude / "full-send").is_symlink())
        self.assertFalse((claude / "full-stop").exists())
        self.assertTrue((claude / "query-tableau-data" / "SKILL.md").is_file())
        backups = list((self.home / ".local/share/astack/skill-backups").glob("*/claude/*"))
        self.assertEqual(sorted(p.name for p in backups), ["full-send", "full-stop"])

    def test_prunes_links_to_removed_skills(self):
        self.run_install()
        stale = self.home / ".agents/skills" / "gone"
        stale.symlink_to(ROOT / "skills" / "gone", target_is_directory=True)
        self.run_install()
        self.assertFalse(stale.is_symlink())

    def test_remove_copies_only_moves_astack_skills(self):
        codex = self.home / ".codex/skills"
        make_skill(codex, "full-send")
        make_skill(codex, "modernize")
        make_skill(codex, "imagegen")
        self.run_install("--remove-copies")
        self.assertEqual(sorted(p.name for p in codex.iterdir()), ["imagegen"])

    def test_review_loop_replaces_old_links_and_backs_up_copies(self):
        agents = self.home / ".agents/skills"
        agents.mkdir(parents=True)
        (agents / "sol-loop").symlink_to(ROOT / "skills/sol-loop", target_is_directory=True)
        make_skill(self.home / ".claude/skills", "sol-loop")
        make_skill(self.home / ".pi/agent/skills", "sol-loop")
        self.run_install("--remove-copies")
        self.assertFalse((agents / "sol-loop").is_symlink())
        for folder in (".agents/skills", ".claude/skills"):
            self.assertEqual((self.home / folder / "review-loop").resolve(), ROOT / "skills/review-loop")
        backups = list((self.home / ".local/share/astack/skill-backups").glob("*/*/sol-loop"))
        self.assertEqual(len(backups), 2)
        self.assertTrue(all((p / "SKILL.md").is_file() for p in backups))
        self.assertEqual(self.run_install("--remove-copies").strip(), "Nothing to change.")

    def test_dry_run_changes_nothing(self):
        out = self.run_install("--dry-run")
        self.assertIn("would link", out)
        self.assertFalse((self.home / ".claude").exists())


if __name__ == "__main__":
    unittest.main()
