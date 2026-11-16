"""Readiness gates use current GitHub evidence and repository reviewer settings."""

import copy
import importlib.machinery
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader(
    "pr_wait", str(ROOT / "skills/babysit-pr/scripts/pr-wait")
)
spec = importlib.util.spec_from_loader(loader.name, loader)
pr_wait = importlib.util.module_from_spec(spec)
loader.exec_module(pr_wait)
HEAD = "a" * 40


def author(login, bot=False):
    return {"login": login, "__typename": "Bot" if bot else "User"}


def review(login="review-bot", head=HEAD, state="COMMENTED", bot=True):
    return {
        "id": login + head,
        "url": "https://example.test/review",
        "body": "",
        "author": author(login, bot),
        "commit": {"oid": head},
        "state": state,
    }


def pull_request():
    return {
        "url": "https://example.test/pr",
        "state": "OPEN",
        "headRefOid": HEAD,
        "baseRefName": "development",
        "mergeStateStatus": "CLEAN",
        "mergeable": "MERGEABLE",
        "isDraft": False,
        "reviewDecision": None,
        "author": author("writer"),
        "viewer": "writer",
        "baseRef": {"target": {"oid": "b" * 40}},
        "comments": {"nodes": []},
        "reviews": {"nodes": [review()]},
        "reviewThreads": {"nodes": []},
    }


class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.patch(pr_wait, "STATE_DIR", Path(self.temp.name))
        self.patch(pr_wait, "required_checks", mock.Mock(return_value={"build"}))
        self.output = io.StringIO()
        self.patch(pr_wait.sys, "stdout", self.output)
        self.patch(pr_wait.sys, "stderr", io.StringIO())
        self.pr = pull_request()
        self.watcher = pr_wait.Watcher(
            "owner/repo",
            1,
            "ready",
            5,
            reviewers=("review-bot",),
        )
        self.watcher.fetch_pr = mock.Mock(side_effect=lambda: copy.deepcopy(self.pr))
        self.watcher.fetch_checks = mock.Mock(
            return_value={
                "build": {
                    "bucket": "pass",
                    "link": "https://example.test/build",
                    "description": "",
                }
            }
        )

    def patch(self, obj, name, value):
        patcher = mock.patch.object(obj, name, value)
        patcher.start()
        self.addCleanup(patcher.stop)

    def finish(self, code):
        self.watcher.poll()
        with self.assertRaises(SystemExit) as result:
            self.watcher.poll()
        self.assertEqual(result.exception.code, code, self.output.getvalue())

    def test_configured_reviewer_completes_readiness(self):
        self.watcher.review_checks = {}
        self.finish(0)
        self.assertIn("ready on aaaaaaa", self.output.getvalue())

    def test_stale_or_unselected_review_never_completes_readiness(self):
        for row in (
            review(head="c" * 40),
            review(login="other[bot]"),
            review(bot=False),
            review(state="DISMISSED"),
            review(state="PENDING"),
        ):
            self.pr["reviews"]["nodes"] = [row]
            self.watcher.poll()
            self.watcher.poll()
        self.assertNotIn("ready on", self.output.getvalue())

    def test_missing_required_check_remains_pending(self):
        self.watcher.fetch_checks.return_value = {}
        self.watcher.poll()
        self.watcher.poll()
        self.assertNotIn("ready on", self.output.getvalue())

    def test_failed_required_check_stops_with_failure(self):
        self.watcher.fetch_checks.return_value["build"]["bucket"] = "fail"
        with self.assertRaises(SystemExit) as result:
            self.watcher.poll()
        self.assertEqual(result.exception.code, 1)

    def test_configured_check_must_finish_successfully_even_after_a_review(self):
        self.watcher.review_checks = {"review-bot": ("review analysis",)}
        self.watcher.fetch_checks.return_value["Review analysis"] = {
            "bucket": "pending",
            "link": "",
            "description": "",
        }
        self.watcher.poll()
        self.watcher.poll()
        self.assertNotIn("ready on", self.output.getvalue())
        self.watcher.fetch_checks.return_value["Review analysis"]["bucket"] = "pass"
        self.watcher.poll()
        with self.assertRaises(SystemExit) as result:
            self.watcher.poll()
        self.assertEqual(result.exception.code, 0)

    def test_failed_review_check_stops_with_failure(self):
        self.watcher.review_checks = {"review-bot": ("review analysis",)}
        self.watcher.fetch_checks.return_value["Review analysis"] = {
            "bucket": "fail",
            "link": "",
            "description": "",
        }
        with self.assertRaises(SystemExit) as result:
            self.watcher.poll()
        self.assertEqual(result.exception.code, 1)

    def test_configured_check_must_appear_before_readiness(self):
        self.watcher.review_checks = {"review-bot": ("review analysis",)}
        self.watcher.poll()
        self.watcher.poll()
        self.assertNotIn("ready on", self.output.getvalue())

    def test_unknown_required_check_state_never_passes(self):
        self.watcher.fetch_checks.return_value["build"]["bucket"] = "unknown"
        self.watcher.poll()
        self.watcher.poll()
        self.assertNotIn("ready on", self.output.getvalue())

    def test_drafts_and_required_human_approvals_block(self):
        self.pr["isDraft"] = True
        self.finish(1)
        self.pr["isDraft"] = False
        self.pr["reviewDecision"] = "REVIEW_REQUIRED"
        with self.assertRaises(SystemExit) as result:
            self.watcher.poll()
        self.assertEqual(result.exception.code, 1)

    def test_human_change_request_blocks_until_approved_or_dismissed(self):
        self.pr["reviews"]["nodes"].append(
            review(login="human", bot=False, state="CHANGES_REQUESTED")
        )
        self.finish(1)
        self.pr["reviews"]["nodes"].append(
            review(login="human", bot=False, state="APPROVED")
        )
        with self.assertRaises(SystemExit) as result:
            self.watcher.poll()
        self.assertEqual(result.exception.code, 0)

    def test_unresolved_threads_and_nonclean_states_block(self):
        self.pr["reviewThreads"]["nodes"] = [
            {
                "isResolved": False,
                "path": "file",
                "line": 1,
                "comments": {
                    "nodes": [
                        {
                            "id": "thread",
                            "url": "https://example.test/thread",
                            "body": "bug",
                            "author": author("human"),
                        }
                    ]
                },
            }
        ]
        self.finish(1)
        self.pr["reviewThreads"]["nodes"] = []
        self.pr["mergeStateStatus"] = "UNKNOWN"
        self.watcher.poll()
        self.pr["mergeStateStatus"] = "BLOCKED"
        with self.assertRaises(SystemExit) as result:
            self.watcher.poll()
        self.assertEqual(result.exception.code, 1)

    def test_advisory_failure_does_not_block_an_otherwise_mergeable_pr(self):
        self.pr["mergeStateStatus"] = "UNSTABLE"
        self.watcher.fetch_checks.return_value["optional-analysis"] = {
            "bucket": "fail",
            "link": "",
            "description": "advisory",
        }
        self.finish(0)

    def test_unknown_mergeability_waits_for_github(self):
        self.pr["mergeable"] = "UNKNOWN"
        self.watcher.poll()
        self.watcher.poll()
        self.assertNotIn("ready on", self.output.getvalue())

    def test_expected_base_and_tested_head_mismatches_stop(self):
        self.watcher.expected_base = "main"
        with self.assertRaises(SystemExit) as result:
            self.watcher.poll()
        self.assertEqual(result.exception.code, 1)
        self.watcher.expected_base = "development"
        self.watcher.expected_head = "c" * 40
        with self.assertRaises(SystemExit) as result:
            self.watcher.poll()
        self.assertEqual(result.exception.code, 1)

    def test_new_head_needs_a_new_stable_check_snapshot(self):
        self.watcher.poll()
        self.pr["headRefOid"] = "c" * 40
        self.pr["reviews"]["nodes"] = [review(head="c" * 40)]
        self.watcher.poll()
        with self.assertRaises(SystemExit) as result:
            self.watcher.poll()
        self.assertEqual(result.exception.code, 0)

    def test_candidate_is_rechecked_before_reporting_ready(self):
        changed = pull_request()
        changed["headRefOid"] = "c" * 40
        self.watcher.fetch_pr.side_effect = [
            copy.deepcopy(self.pr),
            copy.deepcopy(self.pr),
            changed,
        ]
        self.watcher.poll()
        self.watcher.poll()
        self.assertNotIn("ready on", self.output.getvalue())
        self.assertIsNone(self.watcher.prev_snapshot)

    def test_explicit_no_bot_still_checks_human_approval(self):
        self.watcher.reviewers = ()
        self.pr["reviews"]["nodes"] = []
        self.pr["reviewDecision"] = "REVIEW_REQUIRED"
        self.finish(1)

    def test_unconfigured_repository_requires_no_particular_review_service(self):
        default = pr_wait.Watcher("owner/repo", 2, "ready", 5)
        self.assertEqual(default.reviewers, ())
        self.watcher.reviewers = default.reviewers
        self.pr["reviews"]["nodes"] = []
        self.finish(0)

    def test_repository_without_checks_or_a_review_service_can_be_ready(self):
        pr_wait.required_checks.return_value = set()
        self.watcher.reviewers = ()
        self.pr["reviews"]["nodes"] = []
        self.watcher.fetch_checks.return_value = {}
        self.finish(0)

    def test_review_only_repository_uses_its_visible_check_as_the_gate(self):
        pr_wait.required_checks.return_value = set()
        self.watcher.review_checks = {"review-bot": ("review analysis",)}
        self.watcher.fetch_checks.return_value = {
            "Review analysis": {"bucket": "pass", "link": "", "description": ""}
        }
        self.finish(0)

    def test_retargeting_refreshes_required_checks(self):
        self.watcher.until = "any-change"
        self.watcher.poll()
        self.pr["baseRefName"] = "main"
        self.watcher.poll()
        self.assertEqual(
            pr_wait.required_checks.call_args_list,
            [mock.call("owner/repo", "development"), mock.call("owner/repo", "main")],
        )


class ConfigurationTests(unittest.TestCase):
    def test_repository_selection_and_invalid_config(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "config.json"
            with mock.patch.object(pr_wait, "CONFIG_PATH", config):
                self.assertEqual(pr_wait.repository_options("owner/repo"), {})
                config.write_text(
                    json.dumps(
                        {
                            "repos": {
                                "owner/repo": {
                                    "reviewers": ["REVIEW-BOT[bot]"],
                                    "base": "development",
                                }
                            }
                        }
                    )
                )
                self.assertEqual(
                    pr_wait.repository_options("owner/repo"),
                    {"reviewers": ("review-bot",), "base": "development"},
                )
                self.assertEqual(pr_wait.repository_options("different/repo"), {})
                for invalid in (
                    {"repos": []},
                    {"repos": {"owner/repo": {"reviewers": "review-bot"}}},
                    {"repos": {"owner/repo": {"reviewers": [5]}}},
                    {"repos": {"owner/repo": {"base": ""}}},
                ):
                    config.write_text(json.dumps(invalid))
                    with (
                        self.assertRaises(SystemExit) as result,
                        mock.patch("sys.stdout", io.StringIO()),
                    ):
                        pr_wait.repository_options("owner/repo")
                    self.assertEqual(result.exception.code, 2)

    def test_check_aliases_are_repository_specific_and_validated(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "config.json"
            with mock.patch.object(pr_wait, "CONFIG_PATH", config):
                config.write_text(
                    json.dumps(
                        {
                            "repos": {
                                "owner/repo": {
                                    "reviewers": ["REVIEW-BOT[bot]"],
                                    "review_checks": {
                                        "REVIEW-BOT[bot]": ["Review analysis"]
                                    },
                                }
                            }
                        }
                    )
                )
                options = pr_wait.repository_options("owner/repo")
                self.assertEqual(
                    options["review_checks"], {"review-bot": ("review analysis",)}
                )
                watcher = pr_wait.Watcher("owner/repo", 1, "ready", 5, **options)
                self.assertEqual(watcher.bot_name("REVIEW ANALYSIS"), "review-bot")
                self.assertIsNone(watcher.bot_name("Unrelated analysis"))
                self.assertEqual(pr_wait.repository_options("other/repo"), {})
                for aliases in (
                    [],
                    {"review-bot": "Review analysis"},
                    {"review-bot": [5]},
                    {"review-bot": [""]},
                    {"none": ["Review analysis"]},
                ):
                    config.write_text(
                        json.dumps(
                            {"repos": {"owner/repo": {"review_checks": aliases}}}
                        )
                    )
                    with (
                        self.assertRaises(SystemExit) as result,
                        mock.patch("sys.stdout", io.StringIO()),
                    ):
                        pr_wait.repository_options("owner/repo")
                    self.assertEqual(result.exception.code, 2)

    def test_explicit_no_reviewer_is_unambiguous(self):
        self.assertEqual(pr_wait.reviewer_names(["none"]), ())
        self.assertEqual(pr_wait.reviewer_names([]), ())
        with self.assertRaises(ValueError):
            pr_wait.reviewer_names(["none", "review-bot"])


class RequiredCheckDiscoveryTests(unittest.TestCase):
    def test_permission_failures_are_not_treated_as_no_required_checks(self):
        with mock.patch.object(
            pr_wait, "gh_lines", side_effect=pr_wait.GhError("HTTP 403", False)
        ):
            with self.assertRaises(pr_wait.GhError):
                pr_wait.required_checks("owner/repo", "main")

    def test_no_protection_falls_back_to_visible_checks(self):
        with mock.patch.object(
            pr_wait, "gh_lines", side_effect=pr_wait.GhError("HTTP 404", False)
        ):
            self.assertEqual(pr_wait.required_checks("owner/repo", "main"), set())
