---
name: create-verification-skill
description: Generate a project-local verify-<app> skill that drives the real app the way a user does, in any language, framework, or platform. Use when the user says "create verification skill" or "make a verify skill for this repo", or when a project has no scripted way to prove UI, CLI, or service behavior.
---

# Create a verification skill

Adapted from [pstack's create-verification-skill](https://github.com/cursor/plugins/tree/main/pstack/skills/create-verification-skill)
by Lauren Tan (MIT).

Every serious project needs a scripted way to drive the real app and prove
behavior: launch it, use a feature the way a user would, and capture evidence.
This skill generates that as a project-local skill named `verify-<app>`,
tailored to the repo. Write it for the next agent, not for a human. An agent
that has never seen the app will read it cold, in the middle of a task.

`full-send` uses this skill's output for proof, and `maintain-verification-skill`
keeps it current.

## 1. Interview the repo, not the user

Answer these from the codebase. Ask the user only what you cannot observe:

- **What the user touches.** A web UI, a CLI or TUI, a desktop app, an API, a
  mobile app, a library? A repo can have several. Pick the primary one and note
  the rest.
- **Run.** How does the app start locally? Prefer the repo's own documented dev
  command (package scripts, Makefile, README quickstart). Note ports, env vars,
  seed data, and auth.
- **Drive.** How can an agent interact with it from a script? Use existing
  tools first: Playwright or Cypress specs, expect scripts, PTY helpers,
  curl-able endpoints, a debug port. Only then pick a generic recipe: a browser
  over CDP for web and Electron, tmux or a PTY for CLI and TUI, plain HTTP for
  services.
- **Observe.** What evidence can you capture? Screenshots, terminal
  transcripts, response bodies, logs, exit codes, database state.
- **Isolate.** Can two instances run side by side (ports, data dirs,
  profiles)? If not, say so in the generated skill. Refusing to drive a shared
  instance is better than corrupting the user's session.

If the checkout doesn't build or start as-is, fix that first, or report it
precisely, before you generate anything. A skill written against a broken
checkout teaches wrong steps. When a missing asset that doesn't matter blocks
startup (a static dir the API never serves, a sample config), the generated
skill may create it. Mark it as verification setup and remove it in cleanup.

## 2. Pick the location

Agents read project skills from different directories: Claude Code from
`.claude/skills/`, Cursor from `.cursor/skills/`, Codex and pi from
`.agents/skills/`. If the repo already keeps project skills in one of these,
write `verify-<app>/` there. Otherwise write it to `.agents/skills/verify-<app>/`.
Then add a relative symlink to it from each other directory the repo's agents
use, for example
`ln -s ../../.agents/skills/verify-<app> .claude/skills/verify-<app>`.
Keep one real copy so the copies can't drift apart.

## 3. Generate the skill

Write `verify-<app>/SKILL.md` with YAML frontmatter. Set `name: verify-<app>`
and a `description` that names the app, what the user touches, and when to use
the skill. Without frontmatter the skill never loads. Include these sections,
each based on what the interview found, with no placeholders left:

- **Launch.** The exact command that starts the app for verification, and how
  to tell it's ready (a log line, a prompt). Launch must reach a usable state
  from an empty data dir, including migrations and seed data. Ready means
  usable, not just that a process answers. A database health check can pass
  while its init scripts are still running. Include teardown. A short-lived CLI
  or TUI has no server to keep alive. There, launch means build the binary (or
  install deps) once, then start each drive in its own isolated PTY or tmux
  session.
- **Doctor.** One read-only check that answers "is this instance worth
  driving?": the process is up, the version or build is right, we own the
  port, and auth is valid. An agent runs this first whenever anything looks
  off.
- **Drive.** The recipe with real selectors and commands from this repo, not
  examples. Prefer stable handles (ARIA labels, data attributes, prompt
  strings, route paths) over coordinates and tab order.
- **Evidence.** What to capture for a proof and where it goes. State the proof
  standards:
  - Use the real user path, not internal setters or test-only endpoints.
  - Capture the action and the resulting state, not just the final screen.
  - Check side effects (files written, rows inserted, messages sent) as well
    as what's visible.
  - Use mocks only where a production boundary already isolates the external
    system.
  - When the safe path is a dry run or test mode, observe what it skips
    (files, network, git refs) instead of trusting its name. Some dry runs
    still touch the network or open a browser.
- **Cleanup.** How to tear down the instances the run created. Never kill by
  process name. Kill what you started. Cleanup removes instances and scratch
  state, never the evidence. Proof artifacts survive teardown, in a location
  the skill names, outside any directory that cleanup deletes.
- **Helpers.** Any script the skill ships is executable, and the skill body
  shows how to call it. If the reader has to reverse-engineer a helper, it
  doesn't help.

## 4. Seed the feature map

Create `verify-<app>/features/README.md` plus one file per user-facing
feature you can find. Start with the top 3 to 5, from routes, commands, menus,
or docs. Follow the shape in
[`references/feature-map-example/`](references/feature-map-example/): a README
index and one file per feature.

Each file answers, from the user's point of view, what the feature is, how to
reach it, how to drive it, and what end state proves it works. Use these four
H2s: `Sub-features`, `How to get to it (user POV)`,
`Driving it with <tool>`, and `Gotchas`.

If the seed data lacks a precondition that a journey needs, the journey
reports a failure and the reason goes in that feature's `Gotchas`. Never
weaken the journey to make it pass. The map is the repo's maintained
verification source. A proof that drives one convenient entry point is
incomplete when the map lists others.

## 5. Prove the generated skill before handing it over

Run its own instructions end to end once: launch, doctor, drive one mapped
feature, capture evidence, clean up. One feature is enough; the map exists so
later runs can cover the rest. After cleanup, confirm the evidence still exists
at the named location. If cleanup deletes the proof, this step fails.

Fix what fails. Run the generated cleanup after every failed attempt too, so
broken attempts don't leave processes and ports behind. A generated skill that
never ran is a draft, not a deliverable.

If you proved it in a stand-in for the real target (a container in place of a
fresh VM, a local stack in place of a remote one), list every setup step the
stand-in did that the target will not. Those steps stay unverified until a run
on the real target covers them.

## 6. Offer the maintenance loop

Point the user at `maintain-verification-skill` for keeping the map accurate as
the app changes. Suggest a schedule only if they ask.
