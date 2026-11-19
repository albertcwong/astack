# astack

A fork of [tstack](https://github.com/t3dotgg/tstack) with added skills from:

- [pstack](https://github.com/cursor/plugins/tree/main/pstack): `unslop`,
  `create-verification-skill`, and `maintain-verification-skill`.
- [mattpocock/skills](https://github.com/mattpocock/skills):
  `grill-me`, `wait-what`, `track-issue`, and `to-tickets`.
- [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills):
  `code-simplification`, `context-engineering`, `idea-refine`,
  `ci-cd-and-automation`, `frontend-ui-engineering`,
  `api-and-interface-design`, and `browser-testing-with-devtools`.
- [MapleShaw/yt-dlp-downloader-skill](https://github.com/MapleShaw/yt-dlp-downloader-skill):
  `yt-dlp`.

The agent skills I use every day, cleaned up so anyone can use them. They work
in Claude Code, Codex, [pi](https://github.com/badlogic/pi-mono),
[Cursor's `agent` CLI](https://cursor.com/cli), and
[OpenCode](https://opencode.ai). Skills that need other models (`council`,
`review-loop`) call the other CLIs headless (`claude -p`, `codex exec`,
`pi -p`, `agent -p`), so they behave the same from any of these hosts.
OpenCode runs the skills but is not a headless reviewer: `opencode run` has no
read-only mode that its plugins cannot override.

## Skills

| Skill | Say | What it does |
|---|---|---|
| `full-send` | "full send", "full stop" | Takes a change to a merged PR with nobody watching: proves it, reviews it, files it, babysits it, merges it. "Full stop" does the same work but stops when the PR is ready for you to merge. |
| `review-handoff` | "prepare review handoff" (on request only) | Links an issue or task to its worktree, committed candidate and reproducible review setup; checks readiness without assuming a project-specific launcher. |
| `council` | "council" | Gets review from three models from different providers, and loops until they agree. Runs only when you ask. |
| `review-loop` | "review loop" | Reviews a change with one available model, preferring Sonnet, Grok, then Sol. Falls back across agents when quota or access blocks a route. `full-send` uses it before filing. |
| `file-pr` | "file a PR" | Files a short PR that leads with the problem, not an inventory of changes, then fixes CI until the required checks pass. |
| `takeover` | "take over", "modernize" | Finishes someone else's PR, branch, or agent thread, and keeps their credit. Also rebases an old PR and decides if it should still exist. |
| `babysit-pr` | "babysit" | Watches a PR through CI and review bots, and fixes the real findings. |
| `unslop` | "unslop" | Cuts AI tells from prose: docs, PR descriptions, commit messages, comments. |
| `grill-me` | "grill me" | Interviews you in rounds, with a recommended answer for each question, until every decision in a plan is settled. |
| `wait-what` | "wait what" | Re-pitches the last message with context, in short plain sentences. |
| `create-verification-skill` | "create verification skill" | Writes a project `verify-<app>` skill that launches the app, drives it like a user, and captures proof. |
| `maintain-verification-skill` | "maintain verification skill" | Checks a `verify-<app>` skill against the source and the live app, and files one PR of fixes. |
| `code-simplification` | "simplify this" | Makes working code easier to read without changing behavior, one tested step at a time. |
| `context-engineering` | (automatic) | Sets up rules files and manages what the agent keeps in context during long sessions. |
| `idea-refine` | "refine this idea" | Expands a vague idea into options, stress-tests them, and writes a one-pager with a "Not doing" list. |
| `ci-cd-and-automation` | (automatic) | Sets up CI quality gates, deploy strategies, and rollback, and feeds CI failures back to the agent. |
| `frontend-ui-engineering` | (automatic) | Builds responsive, accessible user interfaces that follow the product's design system. |
| `generate-sonarqube-token` | "set up SonarQube auth" | Guides personal token setup and validates the stored credential. |
| `sonarqube-code-quality` | "check the SonarQube quality gate" | Reads existing analysis and helps triage findings with confirmation. |
| `api-and-interface-design` | (automatic) | Designs stable APIs and typed contracts between components and services. |
| `browser-testing-with-devtools` | (automatic) | Verifies real browser behavior, visuals, accessibility, and network activity. |
| `to-tickets` | "split this into tickets" | Breaks an issue, plan, or conversation into small verifiable tickets with blockers, then publishes the approved breakdown. |
| `track-issue` | "track this", "sync the board" | Finds or creates the issue for each change and keeps its Project Status current, setting it from the PR when you don't. |
| `leaving-pr-comments` | (automatic) | Formats comments that an agent posts on your behalf. |
| `yt-dlp` | "download this video" | Downloads videos, playlists, MP3 audio, or subtitles with quality and destination controls. |

Some skills call others. Install the ones they need too:

- `full-send` uses `track-issue`, `review-loop`, `file-pr`, and `babysit-pr`. It uses
  `review-handoff` only when you ask for a handoff record.
- `review-handoff` uses the project's existing task records and verification tools.
  It adds a protocol, not a server launcher or automatic status validator.
- `takeover` uses `file-pr`, `babysit-pr`, and `leaving-pr-comments`.
- `file-pr` and `babysit-pr` use `leaving-pr-comments`.
- `file-pr` uses `unslop`, and `babysit-pr` to wait for checks.
- `file-pr`, `babysit-pr`, and `takeover` use `track-issue`.
- `full-send` uses a project's `verify-<app>` skill when it has one.
- `maintain-verification-skill` uses `file-pr`.
- `frontend-ui-engineering` uses `browser-testing-with-devtools` for live browser proof when available.
- `idea-refine` hands off to `grill-me` once you pick a direction.
- `to-tickets` uses `track-issue` to publish unassigned backlog tickets with parent
  and blocker relationships. It can use `idea-refine` or `grill-me` when the
  outcome or design still needs work. No upstream setup skill is required.

## Install

```bash
git clone https://github.com/albertcwong/astack ~/.local/share/astack/repo
~/.local/share/astack/repo/scripts/install --remove-copies
```

`scripts/install` links each skill into two folders:

- `~/.claude/skills`, which Claude Code reads.
- `~/.agents/skills`, which Codex, Cursor's `agent`, pi and opencode read.

Each skill is a symlink into the clone, so one pull updates every agent:

```bash
git -C ~/.local/share/astack/repo pull && ~/.local/share/astack/repo/scripts/install
```

The old "sol loop" trigger is retired. Say "review loop" for the default
preferences, or "review loop with Sol" to request Sol explicitly.

Run `scripts/install` after each pull. It links new skills, removes links to
deleted ones, and moves any older copies to `~/.local/share/astack/skill-backups/`
instead of deleting them. `--remove-copies` also moves astack copies out of
`~/.codex/skills`, `~/.cursor/skills` and `~/.pi/agent/skills`, so those agents
do not load each skill twice. `--dry-run` prints the changes without making them.

Treat the clone as read-only. Edit skills in a separate checkout and open a PR.

## Requirements

- An authenticated [GitHub CLI](https://cli.github.com) (`gh`).
- `python3` for `babysit-pr`'s `pr-wait` and `track-issue`'s `issue-status`
  scripts. `track-issue` also needs the `project` scope:
  `gh auth refresh -s project`.
- `python3`, `yt-dlp`, and `ffmpeg` for the `yt-dlp` skill (`ffmpeg` is used
  for audio extraction and format merging).
- `review-loop` needs one reachable reviewer. It prefers Sonnet (`claude`,
  `agent`, `pi`), then Grok (`agent`, `pi`), then Sol (`codex`, `agent`, `pi`).
  Install and authenticate at least one supported agent/provider route. Quota
  failures fall through to the next route, unless you pinned a model or agent.
- `council` still needs three providers. Install and sign in to `claude`,
  `codex`, and `agent` for its default members, or configure pi providers.
  `pi --list-models <search>` and `agent --list-models` list model IDs.

## Make them yours

These are starting points. Edit them. Put personal settings, like which models
sit on your council, in your `CLAUDE.md` or `AGENTS.md`, so you can update the
skills without losing them.

## License

[MIT](LICENSE). `unslop` and the verification skills are adapted from pstack,
MIT, copyright 2026 Lauren Tan.
`grill-me`, `wait-what`, `track-issue`, and `to-tickets` are adapted from
mattpocock/skills, MIT, copyright 2026 Matt Pocock. `code-simplification`,
`context-engineering`, `idea-refine`, `ci-cd-and-automation`,
`frontend-ui-engineering`, `api-and-interface-design`, and
`browser-testing-with-devtools` are adapted from addyosmani/agent-skills, MIT,
copyright 2025 Addy Osmani.
`yt-dlp` is adapted from MapleShaw/yt-dlp-downloader-skill, whose README
declares MIT licensing.
