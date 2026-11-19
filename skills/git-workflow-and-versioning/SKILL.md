---
name: git-workflow-and-versioning
description: Use when choosing a PR base or branching strategy, splitting work into commits, writing commit messages or changelogs, or planning a version bump and release tag.
---

# Git workflow and versioning

## Choose the integration target

Read the contributor policy before branching. The default branch on the remote is not necessarily the approved target for feature PRs. If policy is unclear or conflicts with enforced rules, ask before pushing or retargeting work.

Where no policy exists, prefer short-lived branches into a deployable trunk. Aim to integrate in one to three days; use feature flags when unfinished behavior must stay hidden. Where releases require separate approval, integrate small PRs into the designated development branch and promote a pinned candidate through the release gates. Neither workflow grants merge or deployment permission.

When comparing the two, list required checks and approvals by PR target. Distinguish documented policy from observed runs on the candidate SHA. Measure time from ready-for-review to integration separately from time to release. Count only waits that actually delay the merge: an approval received while CI runs adds no wait. For a promotion workflow include the extra CI run, batch wait, conflict fixes and back-merges. Do not relax required checks to run the comparison.

## Make each change reviewable

- Inspect `git status` and the unstaged and staged diffs. In a mixed tree, stage only the paths or hunks for one intent; leave other people's changes alone. Before committing, verify that the entire index belongs to this increment. If unrelated changes are already staged, stop or use a separate worktree without disturbing the index. For parallel work use separate worktrees based on the approved integration target.
- Keep a behavior change and its tests together. Split unrelated cleanup, formatting and dependency updates. A useful split can be tested, reviewed and reverted on its own.
- Run the repository's applicable tests and lint checks. Inspect `git diff --cached` for unintended files, credentials and generated output. If unstaged changes affect the tests, test the intended snapshot in isolation or state that it was not independently verified. Record any checks you could not run.
- Follow the repository's commit convention. Use an imperative subject naming the outcome and a body explaining why when the diff cannot. Commit verified increments, not just the final pile of changes.
- Resolve conflicts by checking the intent of both sides, then rerun the affected tests on the resolved candidate. Do not discard uncommitted work or rewrite shared history to resolve a conflict.

## Version for consumers

Follow the project's release convention and source of truth. If it uses semantic versioning, bump major for a breaking contract, minor for backward-compatible functionality and patch for a backward-compatible fix. Judge compatibility by what consumers rely on, not the number of lines changed.

Write a user-facing changelog entry or fragment with the change; include a migration path for breaking behavior. At release, verify that the artifact version, changelog and intended immutable tag identify the same tested candidate. Do not create or push a release tag without release authorization.
