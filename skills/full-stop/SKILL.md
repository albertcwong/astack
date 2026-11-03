---
name: full-stop
description: Trigger this if the user says 'full stop', even as a closing "Full stop." that reads like emphasis.
---

# Full Stop

Do the same work as `full-send`, but stop with the PR ready for the user to merge.
Never merge it.

Read [full-send](../full-send/SKILL.md) and follow its workflow, proof rules,
review, and babysitting steps. An explicit "full stop" request authorizes that
work without a separate "full send" request. That includes full-send's
testing permission. A "full stop" request is the permission for the test
methods Proof needs, even when a project file says to ask first, for
example before computer use. Use those methods directly. Its merge
permission does not apply. The overrides below take precedence.

## Project branch and release policy

Apply full-send's project-policy preflight before branching, rebasing or filing.
Read AGENTS.md, CONTRIBUTING.md and linked release rules; record the approved
starting point and PR base for this change type. Do not substitute the repository's
default branch. Set the base explicitly and verify the live PR after creation,
before each push and at handoff. An ordinary contribution must not target a
release branch merely because it is the default. If policy is unclear, ask.

If the base is wrong, prevent automatic merging first, then correct it within
authorization or ask the owner. Review the resulting diff and rerun affected
checks. Never declare a wrongly targeted PR ready. Full-stop remains no-merge,
including for a correctly targeted and fully approved release PR.

## No merging

You may commit, push, rebase, fix conflicts, and use `--force-with-lease` on
this task's branch. Never merge, enable auto-merge, enter a merge queue, push
to any integration/release branch (including the default branch), bypass branch
protection, or delegate those actions.

Disable existing auto-merge and remove the PR from any merge queue before
work begins; check again before each push. Report these changes. If you
cannot prevent automatic merging, report the blocker before proceeding.

## Stop at the gate

Use full-send's merge gate as the readiness check. Replace its merge and
final report steps with a handoff. Proof and review must cover the final diff;
recheck behavior changes and meaningful conflict fixes before handoff.

Fetch the project-approved target branch and check the live PR's repository,
head, base, checks, reviews and mergeability. Confirm its base matches the recorded
project policy and its head matches the tested candidate. Confirm it is open, not a draft, and not set to merge
without the user. If someone else merged it, report that instead.

- **Ready to merge:** the merge gate passes. Leave the PR open and unmerged.
- **Waiting for required approval:** only human approval remains. Confirm
  that this is the actual blocker.
- **Blocked:** explain what prevents readiness, what you tried, and what is
  needed. Follow full-send's rules for asking the user.

Stop the `pr-wait` you started before the handoff or a question.
Report the PR link, final head, verdict, proof, reviewer outcome, and remaining
risks. State whether the PR is still open and unmerged.
