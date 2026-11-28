---
name: handoff
description: Write a private continuation note when the user asks to hand work to a fresh agent or session. Not for a candidate review handoff.
---

# Session handoff

Write for an agent that cannot see this conversation. If the request names a
focus (for example, "handoff the failing test"), include only what that agent
needs for that task. For a request to reproduce and review a specific candidate,
use `review-handoff` instead.

Follow the user's private notes convention, including its location and header.
Update the existing task note if there is one. Without a convention, create a
unique, user-private Markdown file in the OS temporary directory, outside the
checkout. Never commit or publish the note. Omit credentials and personal data.

- State the goal, the user's constraints, and the first concrete next step.
- Identify the checkout and branch if relevant. Flag any uncommitted work the
  next agent needs: a commit link alone won't carry it to another machine.
- Record decisions and why they matter. Separate observed results from guesses,
  and name any blocker or check not yet run. Link to issues, diffs and plans
  instead of copying them or pasting a chat transcript.
- End with **Suggested skills**: name the available skills that fit the next step
  and why, or say none. A suggestion is not permission to merge or deploy.

Read the note back, then give the user its absolute path and a prompt for the
next session: `Read <path> and continue with <next step>.` If the destination
cannot access that file, tell the user to transfer it privately first.
