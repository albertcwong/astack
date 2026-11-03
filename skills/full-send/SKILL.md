---
name: full-send
description: Trigger this if the user says 'full send'.
---

# Full Send

If the user triggered this, it's because they are not watching this thread, and
they want you to complete the work end-to-end autonomously. Your updates and
your final message go unread until long after you stop. You own the work from
its current state to a merged PR.

If the user did not explicitly request "full send" in some clear way, do not
assume full autonomy. If they did, everything below applies.

The user grants you permission to:

- Merge the PR once the merge gate passes.
- Force-push the PR's own branch with `--force-with-lease` after a rebase.
- Use the test methods that Proof needs, without asking first.

## Project branch and release policy

Before branching, rebasing or publishing, read the repository's AGENTS.md,
CONTRIBUTING.md and linked contribution/release rules. Determine the change type,
branch starting point, intended PR base, release cadence and required authority.
Record that decision in the work item and PR. The repository's default branch is
not automatically the contribution target. For example, when ordinary work goes
to development and weekly releases go to main, feature/fix/chore/docs PRs must
use development. Full-send does not authorize a release or override project routing.

Fetch and integrate the latest approved target, not a hardcoded main/default
branch. Pass an explicit `--base <approved-target>` to `gh pr create` (or equivalent
API base). This rule also governs file-pr and babysit-pr; their generic default-
branch advice must not redirect work away from the project's approved target.
After creation, before each push and immediately before merge, inspect the live
PR's repository, baseRefName, headRefName and headRefOid. Compare them with the
recorded target and candidate. An incorrect base is a blocker even with green CI.
Disable auto-merge/remove queue enrollment before pushing to a wrongly targeted
PR; correct the target only within authorization, then review the changed diff
and rerun affected checks. If already merged, report it; do not rewrite shared
history or invent a rollback. If policy is missing, ambiguous or conflicts with
an explicit requested target, ask rather than guessing. Never bypass protection.

## Testing permission

A "full send" request is the permission. If a project file or other
instruction says to ask before a test method, or to leave testing to the
user, this request replaces that rule for this task.

That includes ask-first rules for computer use, browser automation,
simulators and devices, running the app or a dev server, screenshots, and
visual checks. Use the method that gives direct proof. List it in the
report.

Rules about how to test still apply. Follow rules that name the correct
command, fixture, or check. This permission only removes the ask-first or
leave-it-to-the-user step. If a preferred method cannot prove the change,
use a gated method under this permission.

It covers only the tests needed for this task. It does not add permission
for the steps under "Asking the user", such as production changes or data
deletion. It also does not bypass a harness or system approval prompt if
one appears.

## Steps

1. **Finish the change.** Complete the goal from the user's request with the
   smallest change that works. Fix the case that happened, not every case
   that could. Create an owned topic branch from the project-approved starting
   point; never implement ordinary work directly on an integration/release branch.
2. **Prove it.** Get proof for every change you made. See "Proof".
3. **Get feedback.** Use the `sol-loop` skill to verify changes.
4. **File the PR** with the `file-pr` skill. Update against the latest
   project-approved target first, preserving shared history. Set the PR base
   explicitly and verify the actual target after creation. Add one short line
   to the description that says how you proved the change.
5. **Babysit the PR** with the `babysit-pr` skill. Fix real findings and CI
   failures. Get proof for each fix before you push it.
6. **Merge** when the merge gate passes.
7. **Report** in your final message: the PR link, the merge commit, your proof,
   and each decision you made for the user.

Stay active from step 1 to step 7. If you end your turn while checks or bots are
pending, the work stops, because nobody will prompt you again. Wait with the
`pr-wait` watcher from `babysit-pr`, so something wakes you when the PR
changes. If you stop before the merge, stop the `pr-wait` you started first.

## Proof

Proof is evidence you observed yourself in this session: command output, a
reproduction, a screenshot. Use the most direct proof the change allows:

- Reproduce the original failure, apply the fix, then watch the same
  reproduction pass.
- Run the checks that the repo's CI runs (typecheck, lint, tests).
- Add one focused test that fails without the fix, when the behavior has none
  and the repo has a test setup.
- For UI and runtime behavior, run the app and look at the change. If the
  repo has a project `verify-<app>` skill, follow it to launch, drive, and
  capture evidence. Green mocked tests do not prove that the user experience
  works. Attach screenshots to the PR when they help and you have a way to
  upload them.

When you cannot find a way to prove a change, you do not have full confidence.
Ask the user.

## Merge gate

Full confidence means all of these are true on the latest commit:

- Your proof covers every change in the diff.
- Required checks are green.
- Review bots have finished, and each finding is fixed or dismissed with a
  written reason.
- No human review still requests changes.
- The actual PR base matches the project-approved target for this change type;
  a release target has explicit release authorization. Recheck immediately before merge.
- The branch is up to date with that approved target, and GitHub reports it as
  mergeable.

Merge with the method the repo uses. Check the allowed methods and recent merged
PRs. If the repo uses a merge queue or auto-merge, stay until GitHub reports the
PR as merged. Merge through branch protection as configured. Never use `--admin`
or other bypasses. You can ignore automated reviews that request "needs human
review" if you have high confidence in your changes.

## Asking the user

A question in a normal message goes unseen, and the thread looks done. To ask
the user something, use the harness's question tool so the thread shows that
it is waiting: `AskUserQuestion` in Claude Code, `request_user_input` in Codex,
or the question tool your harness has. Put all the context in the question:
the PR link, what blocks you, and the options with your recommendation first.

Ask only when you cannot continue alone:

- You cannot prove the change.
- The merge gate cannot pass, and you cannot fix that yourself.
- The next step is outside the grant above: deleting data, touching production,
  changing things outside the repo, closing a PR, or force-pushing any other
  branch.
- The goal is ambiguous in a way that changes the result.
- Another PR makes this one obsolete.

Decide everything else yourself with sensible defaults, and list those decisions
in the report.

If no question tool is available, or the tool returns no answer, take the safe
path: leave the PR open and unmerged, and start your final message with the
question.
