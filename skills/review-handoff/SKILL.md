---
name: review-handoff
description: Record the link between a tracked issue, implementation worktree, committed candidate and reproducible review setup. Use when starting tracked implementation, preparing user review, revising a candidate, or handing off with full-send or full-stop.
---

# Review handoff

Make work discoverable by its issue or task, without asking the reviewer to find
an agent's checkout. Registration records a candidate; it does not prove readiness,
user acceptance, merge, deployment, or adoption.

## Use the project's records

Read the project's contribution, tracking, review and privacy rules first. Use its
existing work item and supported index/transaction mechanism. Do not create a second
registry, overwrite another owner's record, or publish private paths and logs.
Issue tracking and local coordination may use different records; link them.

Use a full issue URL or tracker-qualified identifier, not a bare number. If there
is no issue, follow the project's issue-creation authority. When external writes
are not authorized, use an approved local task identifier and record the missing
issue link. Do not silently create an issue or invent a URL. Preserve the old
identifier as an alias when an issue transfers or is renumbered.

If there is no existing handoff location, agree on one persistent local record
outside tracked source (or in an explicitly ignored directory). A linked Markdown
record is sufficient. Do not invent a launcher command or claim a registration API
exists. Use a project helper only after checking its documented behavior.

## At work start

Record the following before implementation:

- Canonical issue/task reference and link to the existing work item.
- Repository identity, absolute implementation worktree path, branch and base SHA.
- Implementation and review-environment owner, with an accountable human where required.
- Bounded outcome, acceptance checks and non-goals.

Read the record back and verify the checkout and branch match it. Folder names,
board status and an agent's chat message are not substitutes for this mapping.

## Prepare the candidate

Before requesting review or ending a delivery workflow, update the same record:

- Full committed candidate SHA, repository, branch, and implementation worktree.
- Candidate-specific checks, results, evidence locations, failures and unrun checks.
- Absolute review checkout path and its pinned SHA, if runtime review applies.
- Exact working directory, dependency/build commands, fixture preparation, startup,
  verification, restart and stop commands. Use placeholders for secrets, never values.
- Isolated data location and execution mode, prerequisites and known limitations.
- Numbered reviewer actions and expected results.

Record multiple candidates separately under the same task. Mark replaced candidates
superseded; do not silently change the revision being reviewed. New commits require
updated evidence and a new candidate pin, including after conflict resolution.

If runtime review applies, use a persistent, isolated checkout pinned to the
candidate and build assets from that checkout. Do not serve a changing implementation
checkout as a frozen candidate. Refuse a candidate based on uncommitted changes.
Use synthetic or non-production fixtures by default. Do not inherit live credentials,
modify the user's normal data, or replace their running service without authorization.

For local servers, bind to loopback unless explicitly authorized otherwise. Select
an unused port and confirm the actual bind succeeds; a preliminary port check can
race another process. Retry collisions within a bounded limit. Never kill an
unrelated process to reclaim a port. Record URL, process identity (PID plus start
identity or supervisor handle), private log location and verification time.

Verify the expected backend revision, matching built assets where applicable, and
the relevant end-to-end path. A PID, HTTP 200 or successful registration alone is
not readiness. Record the mechanism used to establish revision identity; do not
assume an application exposes a version endpoint.

## State and handoff gate

Map these meanings to the project's states rather than adding competing statuses:

- Registered: the committed candidate and review recipe are recorded.
- Ready: the required checks and actual review path have passed on that candidate;
  a required review server is running and was checked at the reported time.
- Stopped: the recipe is retained, but the server is not running. It is not ready.
- Failed or blocked: record the exact failed prerequisite and the next action.
- Superseded: a newer candidate replaces this one; keep earlier evidence distinct.
- Not applicable: runtime review is unnecessary for this change; give the reason
  and the appropriate document, CLI or other non-server review steps and evidence.

Before handoff and before a merge decision, read back the record and check it
against the current candidate and actual process state. Missing mappings, stale
revisions or an unverified required review path block a ready claim. Preserve the
candidate and report the blocker instead of skipping the record. Do not claim a
required approval while it is still outstanding; project acceptance rules govern.

If a project validator exists, run it and retain its result. Without one, perform
and record these checks manually. This skill is a protocol, not an installed
launcher, scheduler or enforced state-transition validator.

Keep the candidate pinned during review. Before stopping an owned server, update
availability and retain restart instructions; after it stops, remove the ready claim.
On resume, recheck availability and revision before reusing a URL. Do not promise
monitoring while idle or stop processes identified by PID alone after PID reuse.

Finish with the issue/task reference, candidate SHA, handoff-record location,
review availability as last checked, and the verified URL or restart recipe (or
non-runtime review instructions). Report merge and deployment separately. Keep
private local details out of public PRs; publish only approved sanitized evidence.
