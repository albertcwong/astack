"""Planning tickets stay unassigned until implementation actually starts."""
from contextlib import redirect_stdout, redirect_stderr
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from io import StringIO
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
LOADER = SourceFileLoader("issue_status", str(ROOT / "skills/track-issue/scripts/issue-status"))
SPEC = spec_from_loader(LOADER.name, LOADER)
STATUS = module_from_spec(SPEC)
LOADER.exec_module(STATUS)


class CreateIssueTests(unittest.TestCase):
    def setUp(self):
        self.issue = {"number": 42, "title": "A complete outcome", "state": "OPEN",
                      "status": None, "id": "I_42", "item": None}
        self.board = Mock()
        self.board.cfg = dict(STATUS.DEFAULTS)
        self.board.issues.return_value = {42: self.issue}
        self.board.write.side_effect = lambda issue, status: issue.update(status=status)
        self.gh = Mock(return_value="https://github.com/example/repo/issues/42\n")
        self.out = StringIO()

    def run_cli(self, *arguments):
        with patch.object(sys, "argv", ["issue-status", "--repo", "example/repo", *arguments]), \
             patch.object(STATUS, "Board", return_value=self.board), \
             patch.object(STATUS, "config", return_value=self.board.cfg), \
             patch.object(STATUS, "gh", self.gh), redirect_stdout(self.out):
            STATUS.main()

    def test_create_with_parent_and_blockers_is_unassigned_backlog(self):
        title = "Outcome $(touch should-not-run); `literal`"
        self.run_cli("create", "--title", title, "--body-file", "ticket body.md",
                     "--parent", "10", "--blocked-by", "11", "--blocked-by", "12")
        self.assertEqual(self.issue["status"], "Backlog")
        self.gh.assert_called_once_with("issue", "create", "-R", "example/repo", "--title", title,
                                       "--body-file", "ticket body.md", "--parent", "10",
                                       "--blocked-by", "11,12")
        self.assertIn("https://github.com/example/repo/issues/42", self.out.getvalue())
        self.assertIn("created; unassigned", self.out.getvalue())

    def test_create_uses_configured_new_status(self):
        self.board.cfg["new"] = "Planned"
        self.run_cli("create", "--title", "A complete outcome", "--body-file", "ticket.md")
        self.assertEqual(self.issue["status"], "Planned")
        self.gh.assert_called_once_with("issue", "create", "-R", "example/repo", "--title",
                                       "A complete outcome", "--body-file", "ticket.md")

    def test_missing_status_prevents_remote_creation(self):
        self.board.option.side_effect = STATUS.Failure("missing Backlog option")
        with redirect_stderr(StringIO()), self.assertRaises(SystemExit) as error:
            self.run_cli("create", "--title", "Outcome", "--body-file", "ticket.md")
        self.assertEqual(error.exception.code, 1)
        self.gh.assert_not_called()
        self.board.write.assert_not_called()

    def test_created_url_survives_a_project_write_failure(self):
        self.board.write.side_effect = STATUS.Failure("Project permission denied")
        with redirect_stderr(StringIO()), self.assertRaises(SystemExit) as error:
            self.run_cli("create", "--title", "Outcome", "--body-file", "ticket.md")
        self.assertEqual(error.exception.code, 1)
        self.assertIn("Created https://github.com/example/repo/issues/42", self.out.getvalue())
        self.assertEqual(self.gh.call_count, 1)

    def test_created_url_survives_an_issue_lookup_failure(self):
        self.board.issues.return_value = {}
        with redirect_stderr(StringIO()), self.assertRaises(SystemExit):
            self.run_cli("create", "--title", "Outcome", "--body-file", "ticket.md")
        self.assertIn("Created https://github.com/example/repo/issues/42", self.out.getvalue())
        self.board.write.assert_not_called()

    def test_create_failure_does_not_publish_a_success_url_or_change_status(self):
        self.gh.side_effect = STATUS.Failure("gh issue create: unavailable")
        with redirect_stderr(StringIO()), self.assertRaises(SystemExit):
            self.run_cli("create", "--title", "Outcome", "--body-file", "ticket.md")
        self.assertNotIn("Created", self.out.getvalue())
        self.board.write.assert_not_called()

    def test_invalid_creation_arguments_never_contact_github(self):
        for arguments in (("--title", "Outcome"),
                          ("--title", "Outcome", "--body-file", "ticket.md", "--blocked-by", "0"),
                          ("--title", "Outcome", "--body-file", "ticket.md", "--parent", "-1")):
            with self.subTest(arguments=arguments), redirect_stderr(StringIO()), \
                 self.assertRaises(SystemExit) as error:
                self.run_cli("create", *arguments)
            self.assertEqual(error.exception.code, 2)
        self.gh.assert_not_called()

    def test_start_existing_work_still_self_assigns_and_sets_in_progress(self):
        self.run_cli("start", "42")
        self.assertEqual(self.issue["status"], "In progress")
        self.gh.assert_called_once_with("issue", "edit", "42", "-R", "example/repo",
                                       "--add-assignee", "@me")

    def test_start_new_work_retains_parent_and_existing_behavior(self):
        self.run_cli("start", "--title", "Outcome", "--body-file", "ticket.md", "--parent", "10")
        self.assertEqual(self.issue["status"], "In progress")
        self.assertEqual(self.gh.call_count, 2)
        self.assertEqual(self.gh.call_args_list[0].args[-2:], ("--parent", "10"))
        self.assertEqual(self.gh.call_args_list[1].args[-2:], ("--add-assignee", "@me"))

    def test_start_preserves_a_status_set_by_a_person(self):
        self.issue["status"] = "Blocked"
        self.run_cli("start", "42")
        self.assertEqual(self.issue["status"], "Blocked")
        self.board.write.assert_not_called()


if __name__ == "__main__":
    unittest.main()
