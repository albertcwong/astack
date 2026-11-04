# astack

A fork of [tstack](https://github.com/t3dotgg/tstack) with added skills from:

- [pstack](https://github.com/cursor/plugins/tree/main/pstack): `unslop`,
  `create-verification-skill`, and `maintain-verification-skill`.
- [mattpocock/skills](https://github.com/mattpocock/skills/tree/main/skills/productivity):
  `grill-me`, `wait-what`, and `track-issue`.
- [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills):
  `code-review-and-quality`, `code-simplification`, `context-engineering`,
  `idea-refine`, and `ci-cd-and-automation`.

The agent skills I use every day, cleaned up so anyone can use them. They work
in Claude Code, Codex, [pi](https://github.com/badlogic/pi-mono), and
[Cursor's `agent` CLI](https://cursor.com/cli). Skills that need other models
(`council`, `sol-loop`) call the other CLIs headless (`claude -p`,
`codex exec`, `pi -p`, `agent -p`), so they behave the same from any of them.

## Skills

| Skill | Say | What it does |
|---|---|---|
| `full-send` | "full send" | Takes a change to a merged PR with nobody watching: proves it, reviews it, files it, babysits it, merges it. |
| `full-stop` | "full stop" | Same as `full-send`, but stops when the PR is ready for you to merge. |
| `council` | "council" | Gets review from three models from different providers, and loops until they agree. |
| `sol-loop` | "sol loop" | Reviews a change with GPT Sol in a loop until both agents agree. |
| `file-pr` | "file a PR" | Files a short PR that leads with the problem, not an inventory of changes. |
| `takeover` | "take over" | Finishes someone else's PR, branch, or agent thread, and keeps their credit. |
| `babysit-pr` | "babysit" | Watches a PR through CI and review bots, and fixes the real findings. |
| `modernize` | "modernize" | Rebases an old PR and decides if it should still exist. |
| `unslop` | "unslop" | Cuts AI tells from prose: docs, PR descriptions, commit messages, comments. |
| `grill-me` | "grill me" | Interviews you in rounds, with a recommended answer for each question, until every decision in a plan is settled. |
| `wait-what` | "wait what" | Re-pitches the last message with context, in short plain sentences. |
| `create-verification-skill` | "create verification skill" | Writes a project `verify-<app>` skill that launches the app, drives it like a user, and captures proof. |
| `maintain-verification-skill` | "maintain verification skill" | Checks a `verify-<app>` skill against the source and the live app, and files one PR of fixes. |
| `code-review-and-quality` | "review this" | Reviews a change on five axes (correctness, readability, architecture, security, performance) with labeled severities. |
| `code-simplification` | "simplify this" | Makes working code easier to read without changing behavior, one tested step at a time. |
| `context-engineering` | (automatic) | Sets up rules files and manages what the agent keeps in context during long sessions. |
| `idea-refine` | "refine this idea" | Expands a vague idea into options, stress-tests them, and writes a one-pager with a "Not doing" list. |
| `ci-cd-and-automation` | (automatic) | Sets up CI quality gates, deploy strategies, and rollback, and feeds CI failures back to the agent. |
| `track-issue` | "track this", "sync the board" | Finds or creates the issue for each change and keeps its Project Status current, setting it from the PR when you don't. |
| `leaving-pr-comments` | (automatic) | Formats comments that an agent posts on your behalf. |

Some skills call others. Install the ones they need too:

- `full-send` uses `track-issue`, `sol-loop`, `file-pr`, and `babysit-pr`.
- `full-stop` uses `full-send`.
- `takeover` uses `modernize`, `file-pr`, `babysit-pr`, and `leaving-pr-comments`.
- `file-pr`, `babysit-pr`, and `modernize` use `leaving-pr-comments`.
- `file-pr` uses `unslop`.
- `file-pr`, `babysit-pr`, `full-stop`, and `takeover` use `track-issue`.
- `full-send` uses a project's `verify-<app>` skill when it has one.
- `maintain-verification-skill` uses `file-pr`.
- `code-review-and-quality` uses `council` or `sol-loop` for multi-model review,
  `file-pr`, and `leaving-pr-comments`.
- `idea-refine` hands off to `grill-me` once you pick a direction.

## Install

```bash
git clone https://github.com/albertcwong/astack
cp -R astack/skills/* ~/.claude/skills/   # Claude Code
cp -R astack/skills/* ~/.codex/skills/    # Codex
cp -R astack/skills/* ~/.pi/agent/skills/ # pi
cp -R astack/skills/* ~/.cursor/skills/   # Cursor agent
```

## Requirements

- An authenticated [GitHub CLI](https://cli.github.com) (`gh`).
- `python3` for `babysit-pr`'s `pr-wait` and `track-issue`'s `issue-status`
  scripts. `track-issue` also needs the `project` scope:
  `gh auth refresh -s project`.
- `council` and `sol-loop` need other providers' models. Install and sign in
  to `claude`, `codex`, and `pi` (with a provider for Gemini or your third
  council member), or `agent` for Grok. `pi --list-models <search>` and
  `agent --list-models` show which model IDs you can reach.

## Make them yours

These are starting points. Edit them. Put personal settings, like which models
sit on your council, in your `CLAUDE.md` or `AGENTS.md`, so you can update the
skills without losing them.

## License

[MIT](LICENSE). `unslop` and the verification skills are adapted from pstack,
MIT, copyright 2026 Lauren Tan.
`grill-me`, `wait-what`, and `track-issue` are adapted from mattpocock/skills, MIT, copyright
2026 Matt Pocock. `code-review-and-quality`, `code-simplification`,
`context-engineering`, `idea-refine`, and `ci-cd-and-automation` are adapted
from addyosmani/agent-skills, MIT, copyright 2025 Addy Osmani.
