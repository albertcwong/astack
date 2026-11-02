---
name: maintain-verification-skill
description: Audit a project's verify-<app> skill and feature map against the current app. Reads each feature from source, drives every feature live in one session, and ships at most one PR of proven corrections. Use when the user says "maintain verification skill" or "audit the verify skill".
---

# Maintain a verification skill

Adapted from [pstack's maintain-verification-skill](https://github.com/cursor/plugins/tree/main/pstack/skills/maintain-verification-skill)
by Lauren Tan (MIT).

A feature map goes stale as soon as the app changes. This skill keeps a
`verify-<app>` skill made by `create-verification-skill`, or any project-local
verification skill with a feature map, accurate. Work feature by feature, not
sentence by sentence: read every feature file against the source and drive
every feature live, without running every bullet.

## Outcomes

End with one of these, and say which:

- **clean.** Every feature got source and live coverage, and nothing needs
  changing. No branch, no PR.
- **changed.** One PR ships proven doc, helper, or map corrections.
- **blocked.** Coverage could not finish, or a proven fix could not ship
  safely. Say exactly what blocked it.

## Edit scope

Edit only the verification skill's own directory: its `SKILL.md`, `features/`,
and any helper scripts it owns. Never edit product code during a run. When the
map describes behavior the app no longer has, it's either doc drift (fix the
map) or a product regression (report it, and don't hide it by changing the
docs).

## Pass

0. **Find the target.** Look for a project-local skill with launch and drive
   sections and a feature map, usually `verify-*/` under `.agents/skills/`,
   `.claude/skills/`, or `.cursor/skills/`. A symlinked copy is the same
   skill, so edit the real directory. If there are several candidates, ask
   which one. If there are none, stop and point at
   `create-verification-skill` instead of inventing a target.

1. **Check the index.** Read the feature map README and list its sibling
   files. Fix missing, extra, duplicate, or dead entries. Keep this light, with
   no generated inventory.

2. **Read the source.** For each feature file, find out how the feature works
   in the code, flag likely doc drift with file citations, and write one short
   live-verification recipe. Readers never drive the app and never edit files.
   Return, per feature: a summary, the source entry points, likely drift or
   none, and one recipe.

   Run the readers in parallel when you can: native subagents, or headless
   CLIs in read-only mode as in `council` (`claude -p`, `codex exec` with stdin
   from `/dev/null`, `agent -p --mode plan`, `pi -p`). Give each reader the
   repo path and its feature file, because delegates start with no history.
   Without either, read the features yourself, one at a time.

3. **Reconcile.** Confirm every feature file has a summary. Merge overlapping
   recipes into as few app states as practical. Spot-check cited drift, but
   don't re-prove clean claims. Check recent commits for user-facing features
   missing from the map. Call one missing only with a concrete source path.

4. **Drive it live.** This step is required even when the source looks clean.
   You do all of the driving yourself. Follow the verification skill's own
   launch model: one long-lived instance driven in order for servers and UIs,
   or a fresh isolated session per drive for short-lived CLIs. The skill's
   Launch section decides, not this one. Drive every feature at least once.

   Keep three rules for the whole pass, whatever fails:

   1. Never drive an instance you haven't checked since it last did something
      unexpected. Run doctor before the first drive, on each fresh session
      where sessions are the unit, and again after any failed drive. Where
      doctor can't see the failure (a stuck UI state on a healthy process),
      reset to a known state or relaunch.
   2. Evidence captured so far survives every cleanup. Check it at its named
      location instead of assuming.
   3. Nothing a drive started outlives its use. Clean up after failed attempts
      whether the session is stuck, exited, or shared. For a shared instance,
      clean up what you left behind, not the instance.

   A doctor failure caused by a stale skill is drift. Fix it within the edit
   scope and retry once, restarting only what the fix invalidated, before you
   call the pass `blocked`.

   A feature you can't reach counts as `verified-unreachable` only with the
   concrete prerequisite (auth, entitlement, OS, external state) and the route
   you tried. If the map omits that prerequisite, that's drift.

   Drive every helper fix live again before it ships. Do the final teardown
   after the last drive of the run, including those re-proofs, so nothing
   outlives the run. Evidence stays, as the skill says.

5. **Triage.**
   - A wrong or missing user-facing description is doc drift. Fix it.
   - Working behavior the helpers can't drive is a helper gap. Fix it, with
     the same helper rule as generation: scripts are executable, and the skill
     body shows how to call them.
   - App behavior that's broken is a product gap. Record it for the user and
     keep it out of this PR.

6. **Ship or stop.** For `changed`, re-read every changed file, then open one
   PR with the `file-pr` skill. For `clean` or
   `blocked`, open no PR. Report the outcome and the coverage honestly.

Keep short run notes (features covered, unreachable prerequisites, confirmed
drift, outcome) in a scratch location outside the repo. Don't commit them.
