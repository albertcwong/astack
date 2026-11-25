---
name: review-loop
description: Use when the user says "review loop" or "review-loop", or when a workflow requests iterative review before shipping.
---

# Review loop

Have one reviewer check the change, fix real findings, and repeat until the
current change is approved. The workflow is model-agnostic. Keep fixes minimal
and push back on scope creep.

## Budget

- Default: 3 rounds total. Round 1 is full. Later rounds check only
  changed code and open findings.
- Extend to 5 only for security, permissions, auth, data loss, or
  state/concurrency, while a blocker or should stays open with evidence. Or when
  the user asks.
- Stop early if a round returns only nits. Declined nits and comment,
  doc, or format-only fixes need no new round.
- One reviewer at a time. The reviewer must not start subagents or reviewers.
- Keep a ledger: finding id, severity, outcome, model, agent, session ID, and
  usage if returned. Never guess usage or approval.

## 1. Scope

Run `git status --short`. Do not stash, discard, or include unrelated
changes. Limit review to the change paths if they separate cleanly.
Otherwise stop and ask.

Find the base after `git fetch origin`:

- PR: `gh pr view <n> --json baseRefName,headRefOid`. Check out the branch
  only if clean. Confirm `HEAD` is the PR head, or ahead only by this
  change. Base: `git merge-base HEAD origin/<baseRefName>`.
- Local: `git merge-base HEAD origin/<approved-target>`, where the approved
  target is the PR base the project's AGENTS.md or CONTRIBUTING.md names for
  this change type. The default branch is not automatically that target. No
  remote: a base the user names, or `HEAD` for uncommitted changes only.

The change is base to working tree in those paths, with untracked files.
Use one diff command all rounds. State intent and out-of-scope in 1-2
sentences. Run covering checks. Do not send code this change breaks. Note
missing or pre-failing checks in the brief.

## 2. Choose and start a reviewer

Honor an explicitly requested model or agent. Otherwise try these model
families in order, using the listed agents from left to right:

| Preference | Model family | Agents |
| --- | --- | --- |
| 1 | Sonnet | `claude`, `agent`, `pi` |
| 2 | Grok | `agent`, `pi` |
| 3 | Sol | `codex`, `agent`, `pi` |

**Budget fallback takes precedence over this preference table.** If a default agent reports exhausted credits, a monthly limit, or an over-budget response (or the user says it is exhausted), skip that route for this task. Go straight to an authorized OpenAI model via pi rather than testing every other CLI first. A model or agent named in a skill example is a preference, not a user pin. Respect explicit user pins and project restrictions.

Use `pi --list-models` to find an OpenAI model on an approved provider for this repository's data. A configured proxy may list the provider and model separately, for example provider `llm-proxy` and model `openai/<id>`; use `--provider <provider> --model <model-id>` in the pi command below. A listing is not proof of remaining quota: inspect the final assistant result for an actual review, including errors returned in JSON. Do not rotate credentials, raise spending limits, or route around a shared budget. If no eligible route works, report the blocker.

Use the newest available version of the selected family. Resolve model IDs
for the agent you will actually run; IDs are not portable between agents.
`agent --list-models` lists Cursor's models. For Claude, `--model sonnet`
selects its current Sonnet alias; record the resolved model if the result
exposes it, otherwise record the alias without guessing a version. For Codex,
use its model picker or `pi --list-models sol` entries for `openai-codex`, not
IDs from unrelated providers. For pi, use `pi --list-models <family>` and select
an available provider/model pair. Check the selected CLI's `--help` for flags.
Prefer high effort where supported; record actual effort or say it is unknown.

Run one headless reviewer from the repository directory:

| Agent | Initial command |
| --- | --- |
| Claude Code | `claude -p --model <id-or-sonnet> --effort high --permission-mode plan --output-format json "<brief>" </dev/null` |
| Cursor | `agent -p --model <id> --mode plan --trust --workspace <repo> --output-format json "<brief>" </dev/null` |
| Codex | `codex exec -m <id> -c model_reasoning_effort=high -s read-only -C <repo> --json -o <out-file> "<brief>" </dev/null` |
| pi | `pi -p --mode json --model <provider/id> --thinking high --tools read,grep,find,ls --session <session-file> "<brief>" </dev/null` |

For pi, choose a new absolute session-file path under a temporary directory.
Its tool allowlist excludes shell and write tools; supply the diff and check
results as files in the brief because it cannot run Git or tests. Do not describe
this as an OS sandbox. If the provider rejects high thinking, use a supported
level and report it; do not claim high effort from the requested flag alone.

OpenCode is not a reviewer route. `opencode run` has no read-only mode: its
`plan` agent still allows shell commands, and a plugin can override an
agent's deny rules. From OpenCode, start one of the routes above.

Keep review read-only. Never add permission-bypass flags such as `--force`,
`--yolo`, or `--dangerously-skip-permissions`. Do not run a PR watcher inside
the reviewer. Redirect stdin from `/dev/null` so headless runs do not wait for
input. Use one long foreground call, or the host's background-call facility
that delivers completion. Save output to a temporary file.

Save `session_id` from Claude or Cursor JSON, `thread_id` from Codex's
`thread.started` event, or the chosen pi session-file path (its JSON header also
contains an `id`). Continue with the same model and read-only controls:

- Claude: `claude -p --resume <session_id> --model <id-or-sonnet> --effort high --permission-mode plan --output-format json "<brief>" </dev/null`
- Cursor: `agent -p --resume <session_id> --model <id> --mode plan --trust --workspace <repo> --output-format json "<brief>" </dev/null`
- Codex: `codex exec -m <id> -c model_reasoning_effort=high -s read-only -C <repo> resume <thread_id> --json -o <out-file> "<brief>" </dev/null`
- pi: `pi -p --mode json --model <provider/id> --thinking high --tools read,grep,find,ls --session <session-file> "<brief>" </dev/null` (reuse the same file and actual supported thinking level)

### Unavailable reviewers

If a route is missing, unauthenticated, quota-limited, or rejects the selected
model, record the reason. For budget exhaustion use the pi fallback above; otherwise try the next listed route. Do not repeatedly retry
a depleted quota or change account settings. If the user pinned a model or
agent, only try routes that honor that choice; report a blocker if none work.
If all eligible routes fail, report the blocker. A timeout, error, or missing
reply is never approval.

Do not edit scoped files while review runs. Wait for completion; do not poll
or start a second reviewer. Before switching routes after a timeout or error,
cancel the previous run if needed and verify it has stopped. Carry the ledger
and full brief to the replacement; session IDs cannot be reused across agents.
A replacement reviewer reads the whole current diff plus open findings, not
only the last fix. A failed launch is not a completed round; switching reviewers
does not reset the total round budget. Never switch to evade a finding or obtain
an easier approval.

Round 1 brief (the reviewer gets no history):

```
Review only. Do not edit, commit, push, comment on PRs, or start subagents.
Do not run a PR watcher.
Repo: <abs path> Base: <sha> Intent: <intent> Out of scope: <scope> Checks: <results>
See: git diff <base> [-- <paths>]; git status --short (read untracked).
For pi, replace See with absolute paths to the saved diff, status/untracked-file
list, and check results. Read the untracked files listed there too.
Read surrounding code. Find bugs, broken callers, mismatch with intent.
Skip style unless it hides a bug. Hold to the smallest change. Flag code,
tests, or guards the intent does not need. Other paths, rare cases, small
perf, extra compat: nits.
blocker = intended case wrong. should = real bug callers will hit, in intent. nit = rest.
Reply:
VERDICT: APPROVE or CHANGES
R1 [blocker|should|nit] <file>:<line> <claim>. Fix: <suggestion> (stable ids)
```

## 3. Answer findings

Check each finding and severity yourself. Another path, rare case, or
small cost is a nit, whatever label it came with.

- Agree: smallest fix. Prefer delete or narrow over new lock, cache,
  helper, or option. Fix the case that happened. Add one focused test
  that fails without the fix, if intent needs it.
- Disagree: say why, with evidence (file:line, test, output).
- Out of scope or nit: decline in one line. List as follow-up.

Update the ledger. Re-run checks and `git diff --shortstat <base>`. If
review grew the diff, cut first. Do not agree just to end the loop.

## 4. Next round

Start one only if budget remains and a blocker or should is open, behavior code
changed, or approval does not cover the current behavior diff. Resume the saved
session using the matching agent command above. Send the round 1 brief,
the ledger (`fixed:` / `disagree:` / `declined:` + evidence), the same base
diff, and the change since last round. Ask for open ids and changed code only,
unless this is a replacement reviewer, who needs a full review.
Mark each old id `resolved` or `still open: <reason>`.

## 5. Stop and ship

Agreed: APPROVE on the current behavior diff, no blocker or should open,
no concern of your own. Stuck: an item stays disputed after two replies,
or budget ends. Show both sides in 2-3 lines each. The user decides.
Budget end is not approval.

Do not push during the loop. Push after agreement only if the user asked
to push, ship, or update the PR. If you push to a PR, add above the model
blurb:

`Reviewed with review-loop: <N> rounds with <model> via <agent>. Verdict: approved`.

Add `on <effort>` only if verified. If reviewers changed, list the models and
agents per round and which approved the final diff.

Report: rounds, models and agents, fixes prompted by review, diff size
before/after, fixed and declined findings with reasons, unavailable routes,
usage if exposed (else say not), and whether pushed.
