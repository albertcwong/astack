---
name: takeover
description: Take over existing work or bring an old PR up to date. Use when the user asks to take over a PR, branch, or agent thread, requests a takeover, asks to rebase or update an old PR, or says "modernize".
---

# Takeover

Take responsibility for finishing the original goal while preserving the
original contributors' credit. Do not defend an implementation just because
another agent already built it.

Read the source PR, branch, or thread, including review findings and the user's
later corrections. Resolve the handoff to the actual code and current head,
and account for uncommitted work. Treat the handoff as context, not proof.

For a replacement PR, import the original commits onto a new branch and add
your fixes separately. Honor an explicitly requested in-place or stacked
continuation instead. Do not overwrite unrelated work or change the original
PR without authorization.

Preserve Git authorship and existing co-author trailers. Credit the original
contributors in the PR description and link the original PR when there is one.
If the work will be squashed, preserve human author/co-author credit in the
merge commit too, using verified identities rather than guessed emails. Model
attribution is not a substitute for contributor credit.

Bring the continuation up to date against its intended base and current
architecture, as described below. Rework what is necessary to finish the same goal, not
unrelated features. Simplify the implementation without dropping intended
behavior or surfaces. Recheck the source PR too: it may have improved while
you were working.

Independently verify the original failure and realistic workflows, following
repository guidance and permissions. Green mocked tests do not prove the user
experience works. State what remains unverified.

Keep the original work's issue; run `track-issue` with it rather than creating
a new one. When the requested finish includes a PR, use `file-pr` to file or update it,
then `babysit-pr` rather than stopping at creation. Use `leaving-pr-comments`
for replies. Merge or close the original PR only when authorized.

Report what you inherited, what you changed, how you verified it, how credit
was preserved, and any remaining decision.

## Bring an old PR up to date

Use this section alone when the user only asks to rebase, update or "modernize" a
PR. Update the idea, not just the branch: a clean rebase does not prove the PR
still belongs in the product. Updating authorizes rebasing and pushing the PR
branch. It does not authorize merging, closing, changing the base, or adding scope.

1. Fetch the latest base and PR head. Use the PR's actual base and the project's
   approved target, not an assumed `main`. Record the head SHA and merge base.
   Use a disposable worktree if the current one is dirty or in use.
2. State the smallest goal the PR was trying to reach. Then read what landed on
   the base since it diverged, and search merged and open PRs for a replacement.
   Check whether the problem is already solved, whether APIs, schemas or
   ownership changed, and whether landing it would restore old behavior or
   create a second way to do the same thing. No Git conflicts does not mean
   current.
3. Pick a disposition before pushing:
   - **MODERNIZE:** the goal and shape still fit. Rebase, resolve conflicts by
     the PR's intent and the base's newer rules, compare with `git range-diff`,
     run the focused checks, and push with `--force-with-lease` against the head
     you recorded. If the lease fails, fetch and reassess.
   - **REWORK:** the goal fits but the implementation does not. Describe the
     smallest credible rewrite and stop unless the user asked for the rework.
   - **CLOSE:** superseded, obsolete or not worth its cost. Cite the evidence
     and stop. Do not close it without permission. Age alone is not evidence.
4. Lead the report with the disposition and the reason, then base changes,
   conceptual conflicts, the push result, checks and their results, and the
   remaining decision with the PR link. Separate facts from judgment.

Do not post a PR comment unless the user asked for one; use `leaving-pr-comments`
when you do.
