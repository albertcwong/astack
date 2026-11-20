---
name: how
description: Explain how code works, walk through a subsystem before changing it, or identify which package owns a behavior and where a change belongs.
disable-model-invocation: true
---

# How

Answer from the current checkout. Stay read-only: inspect files and search for callers, but do not edit the code, start services, or implement the change. If a name is ambiguous, state which entry point you are tracing.

For a narrow question, trace one concrete example yourself. Start with a caller or test and follow the calls to the result. For a subsystem, split the question into two to four distinct paths, such as request handling, persistence, and response delivery. Trace them yourself, or use parallel read-only explorers if the host supports them. No particular tool, model, or second agent is required.

For each path, identify the entry point, the data passed between components, who owns the decision or state, and what the caller gets back. Record the files and symbols you actually inspected. If two accounts disagree, check the implementation and callers before combining them. Distinguish what the code shows from what you infer; name any boundary you could not trace. Don't invent historical reasons.

Lead with the answer. For a placement question, name the existing owner and the nearest comparable implementation; distinguish current behavior from your recommendation. For a walkthrough, explain the runtime sequence in order and point to the few files and symbols a newcomer should read first. Add a diagram, key concepts, or gotchas only when they clarify the answer. A one-function question rarely needs headings.

Adapted from Lauren Tan's [pstack how](https://github.com/cursor/plugins/tree/main/pstack/skills/how) ([MIT](LICENSE)).
