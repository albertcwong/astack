---
name: track-issue
description: Log work as a GitHub issue and keep its Project Status current. Use at the start of any change that will become a commit or PR, when filing or merging a PR, or when the user says "track this", "track-issue", "sync the board", or "update the board".
---

# Track Issue

Adapted from Matt Pocock's [issue-tracker-github](https://github.com/mattpocock/skills/tree/main/skills/engineering/setup-matt-pocock-skills)
convention (MIT).

Every change has an issue, and the issue's Project Status says where the work
really is. When the user does not set a status, the work sets it. Use
`scripts/issue-status` from this skill's directory (use its absolute path) for
every read and write. Do not hand-write Project mutations or option IDs.

## What this skill may write

Invoking this skill authorizes, for the current repository only: creating an
issue, assigning it to yourself, adding it to the Project, and setting its
Status. Comments, closing, labels, milestones and body edits still need the
user's explicit request. Project rules on comments and closing take
precedence. If a write is blocked by a harness, permission or rate limit,
keep working, keep the change on a pending list, and report it at handoff
with the exact command to run.

## Start

Run this before the first commit of any change, with or without a slash
command.

1. If the user named an issue, use it. Otherwise run
   `issue-status find <key terms>` with words from the error message or the
   request.
2. A likely match is the issue. If unsure, prefer the existing issue, and say
   which one you picked. Never create a duplicate.
3. No match: write a body in the repository's issue format (look at recent
   issues; for a bug, use the user's report, observed message and expected
   behavior). Follow its title convention, for example the next `BUG-NN`.
   Run `issue-status start --title "..." --body-file <file>`, adding
   `--parent <n>` for a sub-issue.
4. Existing issue: `issue-status start <n>`.

Then tell the user in one line: `Tracking #N (<title>). Status: In progress.`

## During the work

Put `Closes #N` in the PR description for the issue the PR finishes. Use
`Refs #N` for a parent or related issue that the PR does not finish. The
script reads these lines on any base branch; GitHub only links closing
keywords on the default branch.

Statuses follow the work on their own. Run `issue-status sync <n> --apply`
after each of these:

| Event | Status |
| --- | --- |
| `start` | In progress |
| Draft PR filed | In progress |
| PR filed or ready for review | In review |
| PR merged, by anyone | Merged |

An automatic change only moves forward and never overwrites a status a
person set, such as Blocked, Ready for user review or User accepted. Set one
of those only when the user names it: `issue-status set <n> "<status>"`.
Close an issue only when the user says so.

## Sync

Run `issue-status sync` (dry run) when the user asks to sync or update the
board, at the start of a session that resumes work, and after the user
merges something you were not watching. Show the planned changes, then run it
again with `--apply`. Report what it could not decide: closed issues with no
merged PR, and PRs that link no issue. Offer to create issues for unlinked
PRs; do not create them without a yes.

## Report

End every handoff or final report with one status line per tracked issue,
for example `#181 BUG-56: In review (PR #182, waiting for your merge)`. List
any pending writes from a blocked call.

## Setup

- `gh auth refresh -s project` once, so `gh` can write Project fields.
- If the repository links more than one Project, or its status names differ
  from In progress, In review and Merged, add an entry to
  `~/.config/track-issue/config.json`. The script's help (`issue-status -h`)
  shows the format. Keep per-repository settings there, not in the
  repository.
- Allow the script in your agent's permission settings if status writes are
  blocked as external writes.
